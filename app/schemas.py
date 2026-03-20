from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Уникальное имя пользователя",
        example="john_doe",
    )
    email: EmailStr = Field(
        ...,
        max_length=50,
        description="Электронная почта пользователя",
        example="john@example.com",
    )
    os: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Операционная система",
        example="linux",
    )
    totaltime: int = Field(
        0, ge=0, description="Общее время использования (в часах)", example=100
    )


class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Имя пользователя",
        example="john_updated",
    )
    email: Optional[EmailStr] = Field(
        None,
        max_length=50,
        description="Электронная почта",
        example="john_new@example.com",
    )
    os: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Операционная система",
        example="ubuntu",
    )
    totaltime: Optional[int] = Field(
        None, ge=0, description="Общее время использования", example=500
    )


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Уникальный идентификатор пользователя", example=1)
    username: str = Field(description="Имя пользователя", example="john_doe")
    email: str = Field(description="Электронная почта", example="john@example.com")
    os: str = Field(description="Операционная система", example="linux")
    totaltime: int = Field(description="Общее время", example=100)
    created_at: datetime = Field(description="Дата создания")
    updated_at: datetime = Field(description="Дата последнего обновления")


class PaginationMeta(BaseModel):
    total: int = Field(description="Общее количество записей", example=25)
    page: int = Field(description="Текущая страница", example=1)
    limit: int = Field(description="Записей на странице", example=10)
    total_pages: int = Field(description="Всего страниц", example=3)


class PaginatedUsers(BaseModel):
    data: List[UserRead] = Field(description="Список пользователей")
    meta: PaginationMeta = Field(description="Метаданные пагинации")
