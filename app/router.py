import math

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user
from app.cache import cache_service
from app.repository import UserRepository
from app.schemas import PaginatedUsers, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


def get_repo():
    return UserRepository()


@router.post("/", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, repo: UserRepository = Depends(get_repo)):
    try:
        user = repo.create(data)
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
