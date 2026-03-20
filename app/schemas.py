import math
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=50)
    os: str = Field(..., min_length=1, max_length=50)
    totaltime: int = Field(0, ge=0)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, min_length=1, max_length=50)
    os: Optional[str] = Field(None, min_length=1, max_length=50)
    totaltime: Optional[int] = Field(None, ge=0)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    os: str
    totaltime: int
    created_at: datetime
    updated_at: datetime


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int


class PaginatedUsers(BaseModel):
    data: List[UserRead]
    meta: PaginationMeta

    @classmethod
    def create(cls, users: list, total: int, page: int, limit: int):
        return cls(
            data=[UserRead.model_validate(u) for u in users],
            meta=PaginationMeta(
                total=total,
                page=page,
                limit=limit,
                total_pages=math.ceil(total / limit) if limit else 0,
            ),
        )
