import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.cache import cache_service
from app.database import get_db
from app.repository import UserRepository
from app.schemas import PaginatedUsers, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

# Общие примеры ошибок
_401 = {
    "description": "Не авторизован",
    "content": {"application/json": {"example": {"detail": "Не авторизован"}}},
}
_403 = {
    "description": "Нет доступа",
    "content": {
        "application/json": {"example": {"detail": "Нет доступа к этому ресурсу"}}
    },
}
_404 = {
    "description": "Не найден",
    "content": {"application/json": {"example": {"detail": "Пользователь не найден"}}},
}
_409 = {
    "description": "Конфликт данных",
    "content": {
        "application/json": {
            "example": {
                "detail": "Пользователь с таким username или email уже существует"
            }
        }
    },
}

_user_example = {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "os": "linux",
    "totaltime": 100,
    "created_at": "2024-01-15T10:30:00+00:00",
    "updated_at": "2024-01-15T10:30:00+00:00",
}


def get_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def invalidate_users_cache(user_id=None):
    # Удаляем все списки
    cache_service.delete_by_pattern("wp:users:list:*")
    # Если передан ID, удаляем профиль конкретного юзера
    if user_id:
        cache_service.delete(f"wp:users:profile:{user_id}")


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    description="Создаёт нового пользователя. Требует авторизации.",
    responses={
        201: {
            "description": "Создан",
            "content": {"application/json": {"example": _user_example}},
        },
        401: _401,
        409: _409,
    },
)
def create_user(data: UserCreate, repo: UserRepository = Depends(get_repo)):
    try:
        user = repo.create(data)
        invalidate_users_cache()
        return user

    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Пользователь с таким email уже существует"
        )


@router.get(
    "/",
    response_model=PaginatedUsers,
    summary="Список пользователей",
    description="Возвращает список пользователей с пагинацией. Soft-deleted записи не возвращаются.",
    responses={
        200: {
            "description": "Список с пагинацией",
            "content": {
                "application/json": {
                    "example": {
                        "data": [_user_example],
                        "meta": {"total": 25, "page": 1, "limit": 10, "total_pages": 3},
                    }
                }
            },
        },
        401: _401,
    },
)
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    repo: UserRepository = Depends(get_repo),
):
    cache_key = f"wp:users:list:page:{page}:limit:{limit}"

    # 1. Пытаемся взять из кеша
    cached_data = cache_service.get(cache_key)
    if cached_data:
        return cached_data

    # 2. Если нет — идем в БД
    offset = (page - 1) * limit
    users, total = repo.get_all(offset, limit)
    total_pages = math.ceil(total / limit) if total > 0 else 0

    # Превращаем в dict для сериализации (т.к. модели SQLAlchemy нельзя напрямую в JSON)
    response_data = {
        "data": [UserRead.from_orm(u).model_dump(mode="json") for u in users],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        },
    }

    # 3. Сохраняем в кеш
    cache_service.set(cache_key, response_data)

    return response_data


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Получить пользователя по ID",
    description="Возвращает пользователя по ID. Soft-deleted записи не возвращаются.",
    responses={
        200: {
            "description": "Найден",
            "content": {"application/json": {"example": _user_example}},
        },
        401: _401,
        404: _404,
    },
)
def get_user(
    user_id: int,
    repo: UserRepository = Depends(get_repo),
    current: dict = Depends(get_current_user),
):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return user


@router.put(
    "/{user_id}",
    response_model=UserRead,
    summary="Полное обновление пользователя",
    description="Обновляет все поля. Можно обновлять только свою запись.",
    responses={
        200: {
            "description": "Обновлён",
            "content": {"application/json": {"example": _user_example}},
        },
        401: _401,
        403: _403,
        404: _404,
        409: _409,
    },
)
def update_user_full(
    user_id: int,
    data: UserCreate,
    repo: UserRepository = Depends(get_repo),
    current: dict = Depends(get_current_user),
):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if user.id != current["user_id"]:
        raise HTTPException(403, "Нет доступа к этому ресурсу")
    try:
        return repo.update_full(user, data)
    except IntegrityError:
        raise HTTPException(409, "Конфликт данных")


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Частичное обновление пользователя",
    description="Обновляет только указанные поля. Можно обновлять только свою запись.",
    responses={
        200: {
            "description": "Обновлён",
            "content": {"application/json": {"example": _user_example}},
        },
        401: _401,
        403: _403,
        404: _404,
        409: _409,
    },
)
def update_user_partial(
    user_id: int,
    data: UserUpdate,
    repo: UserRepository = Depends(get_repo),
    current: dict = Depends(get_current_user),
):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if user.id != current["user_id"]:
        raise HTTPException(403, "Нет доступа к этому ресурсу")
    try:
        return repo.update_partial(user, data)
    except IntegrityError:
        raise HTTPException(409, "Конфликт данных")


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Мягкое удаление пользователя",
    description="Помечает запись как удалённую (soft delete). Можно удалять только свою запись.",
    responses={
        204: {"description": "Удалён"},
        401: _401,
        403: _403,
        404: _404,
    },
)
def delete_user(
    user_id: int,
    repo: UserRepository = Depends(get_repo),
    current: dict = Depends(get_current_user),
):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if user.id != current["user_id"]:
        raise HTTPException(403, "Нет доступа к этому ресурсу")
    repo.soft_delete(user)
    invalidate_users_cache(user_id)
