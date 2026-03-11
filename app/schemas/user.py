import math
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=50)
    os: str = Field(..., min_length=1, max_length=50)
    totaltime: int = Field(..., ge=0)


class UserUpdateFull(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=50)
    os: str = Field(..., min_length=1, max_length=50)
    totaltime: int = Field(..., ge=0)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=1, max_length=50)
    email: str | None = Field(None, min_length=1, max_length=50)
    os: str | None = Field(None, min_length=1, max_length=50)
    totaltime: int | None = Field(None, ge=0)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    os: str
    totaltime: int
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Номер страницы")
    limit: int = Field(10, ge=1, le=100, description="Записей на странице")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int


class PaginatedResponse(BaseModel):
    data: list[UserRead]
    meta: PaginationMeta

    @classmethod
    def create(
        cls,
        items: list,
        total: int,
        page: int,
        limit: int,
    ) -> "PaginatedResponse":
        return cls(
            data=[UserRead.model_validate(item) for item in items],
            meta=PaginationMeta(
                total=total,
                page=page,
                limit=limit,
                total_pages=math.ceil(total / limit) if limit > 0 else 0,
            ),
        )
