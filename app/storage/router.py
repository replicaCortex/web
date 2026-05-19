from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.auth.dependencies import get_current_user
from app.cache import cache_service
from app.config import MAX_FILE_SIZE
from app.storage.service import StorageService

router = APIRouter(prefix="/files", tags=["Files"])


def get_storage_service():
    return StorageService()


@router.post("/", status_code=201)
def upload_file(
    file: UploadFile = File(...),
    current: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
):
    """Загрузка нового файла в хранилище"""

    # 1. Валидация MIME-типа (разрешаем только картинки для аватаров)
    allowed_mimes = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_mimes:
        raise HTTPException(
            status_code=400,
            detail="Недопустимый тип файла. Разрешены только JPG и PNG.",
        )

    # 2. Валидация размера файла
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail="Файл превышает допустимый размер (10 МБ)"
        )

    # 3. Передаем поток файла в наш сервис (файл не читается целиком в память!)
    db_file = storage.upload_file(
        stream=file.file,
        filename=file.filename,
        mimetype=file.content_type,
        size=file.size,
        user_id=current["user_id"],
    )

    return {"fileId": str(db_file.id), "message": "Файл успешно загружен"}


@router.get("/{file_id}")
def download_file(
    file_id: str,
    current: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
):
    """Скачивание файла (только для владельца)"""

    # 1. Проверяем кеш Redis для метаданных
    cache_key = f"wp:files:{file_id}:meta"
    file_meta = cache_service.get(cache_key)

    if not file_meta:
        # Если в кеше нет, идем в БД
        db_file = storage.get_file_metadata(file_id)
        if not db_file:
            raise HTTPException(status_code=404, detail="Файл не найден")

        file_meta = {
            "id": str(db_file.id),
            "user_id": str(db_file.user.id),
            "object_key": db_file.object_key,
            "mimetype": db_file.mimetype,
            "original_name": db_file.original_name,
            "size": db_file.size,
        }
        # Сохраняем в кеш на 300 секунд (как в задании)
        cache_service.set(cache_key, file_meta, ttl=300)

    # 2. Проверка прав доступа (пользователь может качать только свои файлы)
    if file_meta["user_id"] != current["user_id"]:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому файлу")

    # 3. Получаем поток из MinIO
    minio_response = storage.get_file_stream(file_meta["object_key"])
    if not minio_response:
        raise HTTPException(status_code=500, detail="Файл отсутствует в хранилище")

    # 4. Возвращаем StreamingResponse
    # Указываем заголовки, чтобы браузер понимал размер и оригинальное имя файла
    headers = {
        "Content-Disposition": f'attachment; filename="{file_meta["original_name"]}"',
        "Content-Length": str(file_meta["size"]),
    }

    # Читаем файл кусками (по 32 KB), чтобы не забить оперативку (stream vs buffer)
    def iterfile():
        try:
            for chunk in minio_response.stream(32 * 1024):
                yield chunk
        finally:
            minio_response.release_conn()

    return StreamingResponse(
        iterfile(), media_type=file_meta["mimetype"], headers=headers
    )


@router.delete("/{file_id}", status_code=204)
def delete_file(
    file_id: str,
    current: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
):
    """Удаление файла (Soft delete в БД + удаление из MinIO)"""

    db_file = storage.get_file_metadata(file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не найден")

    # Проверка владельца
    if str(db_file.user.id) != current["user_id"]:
        raise HTTPException(status_code=403, detail="Нет доступа")

    # 1. Soft Delete в БД
    db_file.update(deleted_at=datetime.utcnow())

    # 2. Физическое удаление из MinIO
    storage.delete_file(db_file.object_key)

    # 3. Инвалидация кеша
    cache_service.delete(f"wp:files:{file_id}:meta")

    return None
