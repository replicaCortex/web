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

    id: str
    username: str
    email: str
    os: str
    totaltime: int
    avatar_file_id: Optional[str] = None  # <--- ДОБАВИТЬ ЭТУ СТРОКУ
    created_at: datetime
    updated_at: datetime

    @field_validator("id", "avatar_file_id", mode="before")  # <--- ОБНОВИТЬ ДЕКОРАТОР
    @classmethod
    def transform_id(cls, v):
        if v is None:
            return v
        return str(v)


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int


class PaginatedUsers(BaseModel):
    data: List[UserRead]
    meta: PaginationMeta
