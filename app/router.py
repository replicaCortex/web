from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.repository import UserRepository
from app.schemas import PaginatedUsers, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


def get_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, repo: UserRepository = Depends(get_repo)):
    """CREATE"""
    try:
        return repo.create(data)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким username или email уже существует",
        )


@router.get("/", response_model=PaginatedUsers)
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    repo: UserRepository = Depends(get_repo),
):
    """ALL"""
    offset = (page - 1) * limit
    users, total = repo.get_all(offset, limit)
    return PaginatedUsers.create(users, total, page, limit)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, repo: UserRepository = Depends(get_repo)):
    """GET BY ID"""
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user_full(
    user_id: int, data: UserCreate, repo: UserRepository = Depends(get_repo)
):
    """PUT"""
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    try:
        return repo.update_full(user, data)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Конфликт данных")


@router.patch("/{user_id}", response_model=UserRead)
def update_user_partial(
    user_id: int, data: UserUpdate, repo: UserRepository = Depends(get_repo)
):
    """PATCH"""
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    try:
        return repo.update_partial(user, data)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Конфликт данных")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, repo: UserRepository = Depends(get_repo)):
    """DELETE"""
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    repo.soft_delete(user)
