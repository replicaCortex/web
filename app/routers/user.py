from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories import UserRepository
from app.schemas import (
    PaginatedResponse,
    PaginationParams,
    UserCreate,
    UserRead,
    UserUpdate,
    UserUpdateFull,
)
from app.services import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


async def get_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_service),
):
    user = await service.create_user(data)
    return user


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Получить список пользователей с пагинацией",
)
async def get_users(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Записей на странице"),
    service: UserService = Depends(get_service),
):
    params = PaginationParams(page=page, limit=limit)
    return await service.get_users(params)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Получить пользователя по ID",
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_service),
):
    user = await service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserRead,
    summary="Полностью обновить пользователя",
)
async def update_user_full(
    user_id: int,
    data: UserUpdateFull,
    service: UserService = Depends(get_service),
):
    user = await service.update_user_full(user_id, data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
    return user


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Частично обновить пользователя",
)
async def update_user_partial(
    user_id: int,
    data: UserUpdate,
    service: UserService = Depends(get_service),
):
    user = await service.update_user_partial(user_id, data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя (Soft Delete)",
)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_service),
):
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
