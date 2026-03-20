from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.repository import UserRepository
from app.schemas import PaginatedUsers, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


def get_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    description="Создает нового пользователя с указанными данными",
    responses={
        201: {
            "description": "Пользователь успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "os": "linux",
                        "totaltime": 100,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                    }
                }
            },
        },
        409: {
            "description": "Конфликт данных - пользователь с таким username или email уже существует",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Пользователь с таким username или email уже существует"
                    }
                }
            },
        },
        422: {
            "description": "Ошибка валидации данных",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "username"],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    }
                }
            },
        },
    },
)
def create_user(data: UserCreate, repo: UserRepository = Depends(get_repo)):
    try:
        return repo.create(data)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким username или email уже существует",
        )


@router.get(
    "/",
    response_model=PaginatedUsers,
    summary="Получить список пользователей",
    description="Возвращает список пользователей с пагинацией. Пользователи с soft delete не отображаются.",
    responses={
        200: {
            "description": "Успешный ответ",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": 1,
                                "username": "john_doe",
                                "email": "john@example.com",
                                "os": "linux",
                                "totaltime": 100,
                                "created_at": "2024-01-15T10:30:00Z",
                                "updated_at": "2024-01-15T10:30:00Z",
                            }
                        ],
                        "meta": {"total": 25, "page": 1, "limit": 10, "total_pages": 3},
                    }
                }
            },
        }
    },
)
def get_users(
    page: int = Query(1, ge=1, description="Номер страницы (начиная с 1)"),
    limit: int = Query(
        10, ge=1, le=100, description="Количество записей на странице (1-100)"
    ),
    repo: UserRepository = Depends(get_repo),
):
    offset = (page - 1) * limit
    users, total = repo.get_all(offset, limit)
    return PaginatedUsers.create(users, total, page, limit)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Получить пользователя по ID",
    description="Возвращает информацию о пользователе с указанным идентификатором",
    responses={
        200: {
            "description": "Пользователь найден",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "os": "linux",
                        "totaltime": 100,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                    }
                }
            },
        },
        404: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {"example": {"detail": "Пользователь не найден"}}
            },
        },
    },
)
def get_user(user_id: int, repo: UserRepository = Depends(get_repo)):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.put(
    "/{user_id}",
    response_model=UserRead,
    summary="Полное обновление пользователя",
    description="Обновляет все поля пользователя. Если пользователь не существует - возвращает 404.",
    responses={
        200: {
            "description": "Пользователь успешно обновлен",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "john_updated",
                        "email": "john_new@example.com",
                        "os": "ubuntu",
                        "totaltime": 500,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:35:00Z",
                    }
                }
            },
        },
        404: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {"example": {"detail": "Пользователь не найден"}}
            },
        },
        409: {
            "description": "Конфликт данных",
            "content": {"application/json": {"example": {"detail": "Конфликт данных"}}},
        },
    },
)
def update_user_full(
    user_id: int, data: UserCreate, repo: UserRepository = Depends(get_repo)
):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    try:
        return repo.update_full(user, data)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Конфликт данных")


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Частичное обновление пользователя",
    description="Обновляет только указанные поля пользователя",
    responses={
        200: {
            "description": "Пользователь успешно обновлен",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "os": "linux",
                        "totaltime": 999,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:40:00Z",
                    }
                }
            },
        },
        404: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {"example": {"detail": "Пользователь не найден"}}
            },
        },
        409: {
            "description": "Конфликт данных",
            "content": {"application/json": {"example": {"detail": "Конфликт данных"}}},
        },
    },
)
def update_user_partial(
    user_id: int, data: UserUpdate, repo: UserRepository = Depends(get_repo)
):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    try:
        return repo.update_partial(user, data)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Конфликт данных")


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Мягкое удаление пользователя",
    description="Помечает пользователя как удаленного (soft delete). Пользователь не удаляется из БД физически.",
    responses={
        204: {
            "description": "Пользователь успешно удален (возвращается пустой ответ)",
        },
        404: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {"example": {"detail": "Пользователь не найден"}}
            },
        },
    },
)
def delete_user(user_id: int, repo: UserRepository = Depends(get_repo)):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    repo.soft_delete(user)
