from app.models import User
from app.repositories import UserRepository
from app.schemas import (
    PaginatedResponse,
    PaginationParams,
    UserCreate,
    UserUpdate,
    UserUpdateFull,
)


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, data: UserCreate) -> User:
        return await self.repo.create(data)

    async def get_user(self, user_id: int) -> User | None:
        return await self.repo.get_by_id(user_id)

    async def get_users(self, params: PaginationParams) -> PaginatedResponse:
        users, total = await self.repo.get_all(
            offset=params.offset,
            limit=params.limit,
        )
        return PaginatedResponse.create(
            items=users,
            total=total,
            page=params.page,
            limit=params.limit,
        )

    async def update_user_full(self, user_id: int, data: UserUpdateFull) -> User | None:
        return await self.repo.update_full(user_id, data)

    async def update_user_partial(self, user_id: int, data: UserUpdate) -> User | None:
        return await self.repo.update_partial(user_id, data)

    async def delete_user(self, user_id: int) -> bool:
        return await self.repo.soft_delete(user_id)
