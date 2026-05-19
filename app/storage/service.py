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
        self.client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_USE_SSL,
        )
        self.bucket = MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            print(f"Ошибка при проверке/создании бакета MinIO: {e}")

    # INFO: Потоковая загрузка в MinIO
    def upload_file(
        self, stream: BinaryIO, filename: str, mimetype: str, size: int, user_id: str
    ) -> File:
        filename.split(".")[-1] if "." in filename else "bin"
        object_key = f"{uuid.uuid4()}-{filename}"

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_key,
            data=stream,
            length=size,
            content_type=mimetype,
        )

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
        try:
            response = self.client.get_object(self.bucket, object_key)
            return response
        except S3Error as e:
            print(f"MinIO get_object error: {e}")
            return None

    def delete_file(self, object_key: str):
        try:
            self.client.remove_object(self.bucket, object_key)
        except S3Error as e:
            print(f"MinIO remove_object error: {e}")

    def get_file_metadata(self, file_id: str) -> File | None:
        return File.objects(id=file_id, deleted_at=None).first()
