from datetime import datetime

from mongoengine import (
    CASCADE,
    BooleanField,
    DateTimeField,
    Document,
    IntField,
    ReferenceField,
    StringField,
)


class User(Document):
    meta = {"collection": "users"}
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password_hash = StringField()
    salt = StringField()
    os = StringField(default="unknown")
    totaltime = IntField(default=0)
    yandex_id = StringField(unique=True, sparse=True)
    # НОВОЕ ПОЛЕ: Ссылка на файл аватара (указываем строкой 'File', т.к. класс описан ниже)
    avatar_file_id = ReferenceField("File", null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    deleted_at = DateTimeField()


class TokenRecord(Document):
    meta = {"collection": "tokens"}
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    access_token_hash = StringField(required=True)
    refresh_token_hash = StringField(required=True)
    expires_at = DateTimeField(required=True)
    revoked = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)


# НОВАЯ МОДЕЛЬ: Файл (хранит только метаданные, сам файл лежит в MinIO)
class File(Document):
    meta = {"collection": "files"}
    user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)  # Владелец
    original_name = StringField(required=True)  # Оригинальное имя (image.png)
    object_key = StringField(
        required=True, unique=True
    )  # Ключ объекта в MinIO (uuid-image.png)
    size = IntField(required=True)  # Размер в байтах
    mimetype = StringField(required=True)  # Тип файла (image/png)
    bucket = StringField(required=True)  # Бакет (wp-labs-files)
    created_at = DateTimeField(default=datetime.utcnow)  # Время создания
    updated_at = DateTimeField(default=datetime.utcnow)  # Время обновления
    deleted_at = DateTimeField(null=True)  # Для Soft Delete
