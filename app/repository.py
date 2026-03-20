from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def _active(self):
        return self.db.query(User).filter(User.deleted_at.is_(None))

    def create(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self._active().filter(User.id == user_id).first()

    def get_all(self, offset: int, limit: int) -> tuple[list[User], int]:
        query = self._active()
        total = query.count()
        users = query.order_by(User.id).offset(offset).limit(limit).all()
        return users, total

    def update_full(self, user: User, data: UserCreate) -> User:
        for key, value in data.model_dump().items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_partial(self, user: User, data: UserUpdate) -> User:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def soft_delete(self, user: User) -> None:
        user.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
