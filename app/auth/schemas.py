import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class LoginDTO(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordDTO(BaseModel):
    email: EmailStr


class ResetPasswordDTO(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=128)


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    os: str
    totaltime: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
