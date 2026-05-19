import uuid
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.config import (
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    MINIO_USE_SSL,
)
from app.models import File


class StorageService:
    def __init__(self):
        # Инициализация клиента MinIO с данными из .env
        self.client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_USE_SSL,
        )
        self.bucket = MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Проверяет наличие корзины (bucket) и создает её, если нет."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            print(f"Ошибка при проверке/создании бакета MinIO: {e}")

    def upload_file(
        self, stream: BinaryIO, filename: str, mimetype: str, size: int, user_id: str
    ) -> File:
        """
        Загружает файл в MinIO ПОТОКОМ (не буферизируя целиком)
        и сохраняет метаданные в MongoDB.
        """
        # 1. Генерируем уникальный ключ для файла, чтобы избежать перезаписи
        # Например: 123e4567-e89b-12d3-a456-426614174000-avatar.png
        filename.split(".")[-1] if "." in filename else "bin"
        object_key = f"{uuid.uuid4()}-{filename}"

        # 2. Загружаем стрим прямо в MinIO
        # (В FastAPI `stream` это SpooledTemporaryFile, он работает как поток)
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_key,
            data=stream,
            length=size,
            content_type=mimetype,
        )

        # 3. Сохраняем метаданные в БД
        new_file = File(
            user=user_id,
            original_name=filename,
            object_key=object_key,
            size=size,
            mimetype=mimetype,
            bucket=self.bucket,
        )
        new_file.save()
        return new_file

    def get_file_stream(self, object_key: str):
        """Получает поток файла из MinIO (для скачивания)"""
        try:
            response = self.client.get_object(self.bucket, object_key)
            return response
        except S3Error as e:
            print(f"MinIO get_object error: {e}")
            return None

    def delete_file(self, object_key: str):
        """Физически удаляет файл из MinIO"""
        try:
            self.client.remove_object(self.bucket, object_key)
        except S3Error as e:
            print(f"MinIO remove_object error: {e}")

    def get_file_metadata(self, file_id: str) -> File | None:
        """Ищет метаданные файла в MongoDB по его ID (с учетом soft delete)"""
        return File.objects(id=file_id, deleted_at=None).first()
