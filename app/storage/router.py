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


# INFO: Валидация MIME-типа и размера
@router.post("/", status_code=201)
def upload_file(
    file: UploadFile = File(...),
    current: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
):

    allowed_mimes = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_mimes:
        raise HTTPException(
            status_code=400,
            detail="Недопустимый тип файла. Разрешены только JPG и PNG.",
        )

    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail="Файл превышает допустимый размер (10 МБ)"
        )

    db_file = storage.upload_file(
        stream=file.file,
        filename=file.filename,
        mimetype=file.content_type,
        size=file.size,
        user_id=current["user_id"],
    )

    return {"fileId": str(db_file.id), "message": "Файл успешно загружен"}


# INFO: Проверка прав владельца файла
@router.get("/{file_id}")
def download_file(
    file_id: str,
    current: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
):

    cache_key = f"wp:files:{file_id}:meta"
    file_meta = cache_service.get(cache_key)

    if not file_meta:
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
        cache_service.set(cache_key, file_meta, ttl=300)

    if file_meta["user_id"] != current["user_id"]:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому файлу")

    minio_response = storage.get_file_stream(file_meta["object_key"])
    if not minio_response:
        raise HTTPException(status_code=500, detail="Файл отсутствует в хранилище")

    headers = {
        "Content-Disposition": f'attachment; filename="{file_meta["original_name"]}"',
        "Content-Length": str(file_meta["size"]),
    }

    # INFO: Потоковая отдача файла клиенту
    def iterfile():
        try:
            for chunk in minio_response.stream(32 * 1024):
                yield chunk
        finally:
            minio_response.release_conn()

    return StreamingResponse(
        iterfile(), media_type=file_meta["mimetype"], headers=headers
    )


# INFO: Событийная инвалидация кэша
@router.delete("/{file_id}", status_code=204)
def delete_file(
    file_id: str,
    current: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
):

    db_file = storage.get_file_metadata(file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не найден")

    if str(db_file.user.id) != current["user_id"]:
        raise HTTPException(status_code=403, detail="Нет доступа")

    db_file.update(deleted_at=datetime.utcnow())

    storage.delete_file(db_file.object_key)

    cache_service.delete(f"wp:files:{file_id}:meta")

    return None
