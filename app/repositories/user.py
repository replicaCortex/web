from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreate, UserUpdate, UserUpdateFull


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _not_deleted():
        return User.deleted_at.is_(None)

    async def create(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id, self._not_deleted())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username, self._not_deleted())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, offset: int = 0, limit: int = 10) -> tuple[list[User], int]:
        count_query = select(func.count()).select_from(User).where(self._not_deleted())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = (
            select(User)
            .where(self._not_deleted())
            .order_by(User.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def update_partial(self, user_id: int, data: UserUpdate) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_full(self, user_id: int, data: UserUpdateFull) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        update_data = data.model_dump()
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def soft_delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user is None:
            return False

        user.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True
