import hashlib
import os
import time

import httpx
import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.jwt_utils import (
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_refresh_token,
)
from app.auth.repository import AuthRepository
from app.config import (
    JWT_ACCESS_SECRET,
    YANDEX_CALLBACK_URL,
    YANDEX_CLIENT_ID,
    YANDEX_CLIENT_SECRET,
)


class AuthService:
    def __init__(self, db: Session):
        self.repo = AuthRepository(db)

    @staticmethod
    def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
        if not salt:
            salt = os.urandom(16).hex()

        salted_password = password + salt
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        return hashed, salt

    @staticmethod
    def _verify_password(password: str, hashed: str, salt: str) -> bool:
        check_hash, _ = AuthService._hash_password(password, salt)
        return check_hash == hashed

    def _issue_tokens(self, user_id: int) -> tuple[str, str]:
        access = create_access_token(user_id)
        refresh = create_refresh_token(user_id)
        self.repo.save_token(user_id, hash_token(access), hash_token(refresh))
        return access, refresh

    def register(self, username: str, email: str, password: str):
        if self.repo.get_user_by_email(email):
            raise HTTPException(409, "Пользователь с таким email уже существует")

        hashed, salt = self._hash_password(password)
        user = self.repo.create_user(username, email, hashed, salt)
        return user

    def login(self, email: str, password: str) -> tuple:
        user = self.repo.get_user_by_email(email)
        if not user or not user.password_hash:
            raise HTTPException(401, "Неверные учётные данные")

        if not self._verify_password(password, user.password_hash, user.salt):
            raise HTTPException(401, "Неверные учётные данные")

        access, refresh = self._issue_tokens(user.id)
        return user, access, refresh

    def refresh(self, refresh_token: str) -> tuple:
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(401, "Невалидный refresh token")

        record = self.repo.find_token_by_refresh_hash(hash_token(refresh_token))
        if not record:
            raise HTTPException(401, "Refresh token отозван")

        self.repo.revoke_token(record)
        user = self.repo.get_user_by_id(payload["sub"])
        if not user:
            raise HTTPException(401, "Пользователь не найден")

        access, refresh = self._issue_tokens(user.id)
        return user, access, refresh

    def logout(self, access_token: str):
        record = self.repo.find_token_by_access_hash(hash_token(access_token))
        if record:
            self.repo.revoke_token(record)

    def logout_all(self, user_id: int):
        self.repo.revoke_all_user_tokens(user_id)

    def get_profile(self, user_id: int):
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "Пользователь не найден")
        return user

    def forgot_password(self, email: str) -> str:
        user = self.repo.get_user_by_email(email)
        if not user:
            return "Если email существует, инструкции отправлены"

        reset_token = jwt.encode(
            {"sub": user.id, "type": "reset", "exp": int(time.time()) + 900},
            JWT_ACCESS_SECRET,
            algorithm="HS256",
        )
        return reset_token

    def reset_password(self, token: str, new_password: str):
        try:
            payload = jwt.decode(token, JWT_ACCESS_SECRET, algorithms=["HS256"])
            if payload.get("type") != "reset":
                raise HTTPException(400, "Невалидный токен сброса")

            user = self.repo.get_user_by_id(payload["sub"])
            if not user:
                raise HTTPException(404, "Пользователь не найден")

            hashed, salt = self._hash_password(new_password)
            self.repo.update_password(user, hashed, salt)
        except Exception:
            raise HTTPException(400, "Невалидный или просроченный токен сброса")

    @staticmethod
    def get_yandex_auth_url(state: str) -> str:
        return (
            f"https://oauth.yandex.ru/authorize?"
            f"response_type=code&client_id={YANDEX_CLIENT_ID}"
            f"&redirect_uri={YANDEX_CALLBACK_URL}&state={state}"
        )

    def handle_yandex_callback(self, code: str) -> tuple:
        resp = httpx.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": YANDEX_CLIENT_ID,
                "client_secret": YANDEX_CLIENT_SECRET,
            },
        )
        if resp.status_code != 200:
            raise HTTPException(400, "Ошибка получения токена от Yandex")

        ya_token = resp.json()["access_token"]

        info = httpx.get(
            "https://login.yandex.ru/info",
            headers={"Authorization": f"OAuth {ya_token}"},
        ).json()

        yandex_id = info["id"]
        email = info.get("default_email", f"{yandex_id}@yandex.ru")
        username = info.get("login", f"yandex_{yandex_id}")

        user = self.repo.get_user_by_yandex_id(yandex_id)
        if not user:
            user = self.repo.get_user_by_email(email)
            if user:
                user.yandex_id = yandex_id
                self.repo.db.commit()
            else:
                user = self.repo.create_oauth_user(username, email, yandex_id)

        access, refresh = self._issue_tokens(user.id)
        return user, access, refresh
