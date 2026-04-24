from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    os: str
    totaltime: int = 0


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    os: Optional[str] = None
    totaltime: Optional[int] = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Мы называем поле id, а валидатор сам заберет его из Mongo
    id: str
    username: str
    email: str
    os: str
    totaltime: int
    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def transform_id(cls, v):
        # Превращаем ObjectId в обычную строку
        return str(v)


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int


class PaginatedUsers(BaseModel):
    data: List[UserRead]
    meta: PaginationMeta
