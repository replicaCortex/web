import math

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.dependencies import get_current_user
from app.cache import cache_service
from app.repository import UserRepository
from app.schemas import PaginatedUsers, ProfileUpdateDTO, UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


def get_repo():
    return UserRepository()


@router.post("/", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, repo: UserRepository = Depends(get_repo)):
    try:
        user = repo.create(data)
        cache_service.delete_by_pattern("wp:users:list:*")
        return UserRead.model_validate(user)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(409, "Конфликт: пользователь уже существует")


@router.get("/", response_model=PaginatedUsers)
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    repo: UserRepository = Depends(get_repo),
):
    cache_key = f"wp:users:list:page:{page}:limit:{limit}"

    cached_data = cache_service.get(cache_key)
    if cached_data:
        return cached_data

    offset = (page - 1) * limit
    users, total = repo.get_all(offset, limit)
    total_pages = math.ceil(total / limit) if total > 0 else 0

    response_data = {
        "data": [UserRead.model_validate(u).model_dump(mode="json") for u in users],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        },
    }

    cache_service.set(cache_key, response_data)

    return response_data


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, repo: UserRepository = Depends(get_repo)):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "Не найден")
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: str,
    repo: UserRepository = Depends(get_repo),
    current=Depends(get_current_user),
):
    user = repo.get_by_id(user_id)
    if not user or str(user.id) != current["user_id"]:
        raise HTTPException(403, "Нет доступа")
    repo.soft_delete(user)
    cache_service.delete_by_pattern("wp:users:list:*")
    cache_service.delete(f"wp:users:profile:{user_id}")

    # --- ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ---


profile_router = APIRouter(prefix="/profile", tags=["Profile"])


@profile_router.get("/", response_model=UserRead)
def get_my_profile(
    current: dict = Depends(get_current_user), repo: UserRepository = Depends(get_repo)
):
    """Получение текущего профиля"""
    user = repo.get_by_id(current["user_id"])
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return user


@profile_router.post("/", response_model=UserRead)
def update_profile(
    data: ProfileUpdateDTO,
    current: dict = Depends(get_current_user),
    repo: UserRepository = Depends(get_repo),
):
    """Обновление профиля (установка аватара)"""
    user_id = current["user_id"]
    user = repo.get_by_id(user_id)

    if not user:
        raise HTTPException(404, "Пользователь не найден")

    # 1. Если передали ID файла для аватара, проверяем его!
    if data.avatarFileId:
        from app.models import File

        # Ищем файл в БД
        db_file = File.objects(id=data.avatarFileId, deleted_at=None).first()
        if not db_file:
            raise HTTPException(404, "Файл не найден")

        # САМАЯ ВАЖНАЯ ПРОВЕРКА - принадлежит ли файл этому юзеру?
        if str(db_file.user.id) != user_id:
            raise HTTPException(403, "У вас нет прав на использование этого файла")

        user.avatar_file_id = db_file.id

    # 2. Обновляем остальные текстовые поля (если они есть)
    if data.username:
        user.username = data.username
    if data.os:
        user.os = data.os
    if data.totaltime is not None:
        user.totaltime = data.totaltime

    user.save()

    # 3. Инвалидируем (сбрасываем) кеш профиля и списка юзеров
    cache_service.delete(f"wp:users:profile:{user_id}")
    cache_service.delete_by_pattern("wp:users:list:*")

    return user
