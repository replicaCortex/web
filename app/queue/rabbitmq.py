import datetime
import json
import traceback
import uuid

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.cache import cache_service
from app.config import (
    QUEUE_USER_REGISTERED,
    RABBITMQ_HOST,
    RABBITMQ_PASS,
    RABBITMQ_PORT,
    RABBITMQ_USER,
)
from app.mail.service import mail_service


class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
        self.connection = await aio_pika.connect_robust(url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)

        dlx = await self.channel.declare_exchange(
            "app.dlx", aio_pika.ExchangeType.DIRECT, durable=True
        )
        dlq = await self.channel.declare_queue(
            f"{QUEUE_USER_REGISTERED}.dlq", durable=True
        )
        await dlq.bind(dlx, routing_key="user.registered")

        exchange = await self.channel.declare_exchange(
            "app.events", aio_pika.ExchangeType.DIRECT, durable=True
        )
        queue = await self.channel.declare_queue(
            QUEUE_USER_REGISTERED,
            durable=True,
            arguments={
                "x-dead-letter-exchange": "app.dlx",
                "x-dead-letter-routing-key": "user.registered",
            },
        )
        await queue.bind(exchange, routing_key="user.registered")

        print("✅ RabbitMQ: Обменники и очереди успешно объявлены")

    async def disconnect(self):
        if self.connection:
            await self.connection.close()

    async def publish_user_registered(self, user_id: str, email: str, username: str):
        exchange = await self.channel.get_exchange("app.events")

        event_id = str(uuid.uuid4())
        payload = {
            "eventId": event_id,
            "eventType": "user.registered",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "payload": {"userId": user_id, "email": email, "displayName": username},
            "metadata": {"sourceService": "auth-service"},
        }

        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await exchange.publish(message, routing_key="user.registered")

    async def start_consuming(self):
        queue = await self.channel.get_queue(QUEUE_USER_REGISTERED)
        await queue.consume(self._process_message)

    async def _process_message(self, message: AbstractIncomingMessage):
        body = json.loads(message.body.decode())
        event_id = body.get("eventId")
        payload = body.get("payload", {})

        if cache_service.get(f"wp:events:processed:{event_id}"):
            await message.ack()
            return

        attempt_key = f"wp:events:attempts:{event_id}"
        attempt = cache_service.client.incr(attempt_key)

        try:
            await mail_service.send_welcome_email(
                to_email=payload.get("email"), username=payload.get("displayName")
            )

            cache_service.set(f"wp:events:processed:{event_id}", "done", ttl=86400)
            cache_service.client.delete(attempt_key)
            await message.ack()

        except Exception as e:
            traceback.print_exc()

            if attempt >= 3:
                await message.reject(requeue=False)
                cache_service.client.delete(attempt_key)
            else:
                await message.reject(requeue=True)


rabbit_service = RabbitMQService()
