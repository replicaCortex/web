from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories import UserRepository
from app.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


async def get_repo(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepository(session)


# ═════════════════════════════════════════════════════════════════
# CREATE — POST /users
# ═════════════════════════════════════════════════════════════════
@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    description="Создаёт нового пользователя. Username и email должны быть уникальными.",
)
async def create_user(
    data: UserCreate,
    repo: UserRepository = Depends(get_repo),
):
    from sqlalchemy.exc import IntegrityError

    try:
        user = await repo.create(data)
        return user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь с таким username или email уже существует",
        )


# ═════════════════════════════════════════════════════════════════
# READ ALL — GET /users
# ═════════════════════════════════════════════════════════════════
@router.get(
    "/",
    response_model=list[UserRead],
    summary="Получить список пользователей",
    description="Возвращает список пользователей с пагинацией.",
)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    repo: UserRepository = Depends(get_repo),
):
    users = await repo.get_all(skip=skip, limit=limit)
    return users


# ═════════════════════════════════════════════════════════════════
# READ ONE — GET /users/{user_id}
# ═════════════════════════════════════════════════════════════════
@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Получить пользователя по ID",
)
async def get_user(
    user_id: int,
    repo: UserRepository = Depends(get_repo),
):
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
    return user


# ═════════════════════════════════════════════════════════════════
# UPDATE — PATCH /users/{user_id}
# ═════════════════════════════════════════════════════════════════
@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Обновить пользователя",
    description="Частичное обновление. Передайте только те поля, которые нужно изменить.",
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    repo: UserRepository = Depends(get_repo),
):
    from sqlalchemy.exc import IntegrityError

    try:
        user = await repo.update(user_id, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким username или email уже существует",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
    return user


# ═════════════════════════════════════════════════════════════════
# DELETE — DELETE /users/{user_id}
# ═════════════════════════════════════════════════════════════════
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
)
async def delete_user(
    user_id: int,
    repo: UserRepository = Depends(get_repo),
):
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id={user_id} не найден",
        )
