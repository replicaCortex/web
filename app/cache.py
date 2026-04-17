import json

import redis

from app.config import CACHE_TTL, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT


class CacheService:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,  # Чтобы получать строки, а не байты
        )

    def set(self, key: str, value: dict | list, ttl: int = CACHE_TTL):
        self.client.set(key, json.dumps(value), ex=ttl)

    def get(self, key: str):
        data = self.client.get(key)
        return json.loads(data) if data else None

    def delete(self, key: str):
        self.client.delete(key)

    def delete_by_pattern(self, pattern: str):
        keys = self.client.keys(pattern)
        if keys:
            self.client.delete(*keys)


cache_service = CacheService()
