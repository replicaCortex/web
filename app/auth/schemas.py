import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterDTO(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Уникальное имя пользователя, от 3 до 50 символов",
        example="john_doe",
    )
    email: EmailStr = Field(
        ..., description="Электронная почта пользователя", example="john@example.com"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Пароль пользователя, от 6 до 128 символов. Должен содержать хотя бы одну цифру",
        example="securePass123",
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class LoginDTO(BaseModel):
    email: EmailStr = Field(
        ..., description="Электронная почта пользователя", example="john@example.com"
    )
    password: str = Field(
        ..., description="Пароль пользователя", example="securePass123"
    )


class ForgotPasswordDTO(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Электронная почта, на которую будет отправлена ссылка для сброса пароля",
        example="john@example.com",
    )


class ResetPasswordDTO(BaseModel):
    token: str = Field(
        ...,
        description="Токен сброса пароля, полученный по электронной почте",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dr9E8RkC0jP",
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Новый пароль пользователя, от 6 до 128 символов",
        example="newSecurePass456",
    )

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class UserProfileResponse(BaseModel):
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


class MessageResponse(BaseModel):
    message: str = Field(
        ...,
        description="Сообщение о результате выполнения операции",
        example="Операция выполнена успешно",
    )
