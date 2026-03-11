from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100):
        query = select(User).order_by(User.id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, user_id: int, data: UserUpdate) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        await self.session.delete(user)
        await self.session.commit()
        return True


# HTTP-запрос → Router → Repository → SQLAlchemy Session → БД
#                 ↓            ↓
#            Pydantic      SQLAlchemy
#            Schema         Model
#
# Пример CREATE:
#     POST /users {"username": "john"}
#         ↓
#     Router: валидирует через UserCreate (Pydantic)
#         ↓
#     Repository.create(data):
#         User(**data.model_dump())   → SQLAlchemy объект
#         session.add(user)           → помечен для INSERT
#         session.commit()            → INSERT INTO users ...
#         session.refresh(user)       → SELECT (получить id)
#         return user                 → SQLAlchemy объект
#         ↓
#     Router: преобразует в UserRead (Pydantic)
#         ↓
#     HTTP-ответ: {"id": 1, "username": "john", ...}
