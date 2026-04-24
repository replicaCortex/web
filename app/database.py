from mongoengine import connect

from app.config import MONGO_URI


def init_db():
    # Просто подключаемся к базе
    connect(host=MONGO_URI)


def get_db():
    # В MongoDB (MongoEngine) соединение глобальное,
    # этот генератор оставляем для совместимости с Depends в роутах
    yield None
