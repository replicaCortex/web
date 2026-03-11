from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: str
    os: str
    totaltime: int


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    os: str | None = None
    totaltime: int | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    os: str
    totaltime: int
