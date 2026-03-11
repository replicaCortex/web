from operator import index

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    os: Mapped[str] = mapped_column(String(50), index=True)
    totaltime: Mapped[int] = mapped_column(Integer, index=True)

    def __repr__(self) -> str:
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
