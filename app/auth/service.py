import hashlib
import os
import uuid

import httpx
from fastapi import HTTPException

from app.auth.jwt_utils import (
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_refresh_token,
)
from app.auth.repository import AuthRepository
from app.cache import cache_service
from app.config import (
    JWT_ACCESS_EXPIRATION,
    YANDEX_CALLBACK_URL,
    YANDEX_CLIENT_ID,
    YANDEX_CLIENT_SECRET,
)


class AuthService:
    def __init__(self):
        self.repo = AuthRepository()

    def _hash_password(self, password: str, salt: str = None) -> tuple[str, str]:
        """Хеширует пароль с солью (используем pbkdf2_hmac)"""
        if not salt:
            salt = os.urandom(16).hex()
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
        return pwd_hash, salt

    def _generate_tokens(self, user) -> tuple[str, str]:
        """Генерирует пару токенов и сохраняет их в БД (в виде хешей)"""
        access_token, jti = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        self.repo.save_token(
            user_id=user,
            access_hash=hash_token(access_token),
            refresh_hash=hash_token(refresh_token),
        )

        # --- ИСПРАВЛЕНИЕ: Сохраняем сессию в Redis ---
        cache_key = f"wp:auth:user:{user.id}:access:{jti}"
        cache_service.set(cache_key, "active", ttl=JWT_ACCESS_EXPIRATION * 60)
        # ---------------------------------------------

        return access_token, refresh_token

    def register(self, username: str, email: str, password: str):
        # Проверяем, существует ли уже пользователь с таким email
        if self.repo.get_user_by_email(email):
            raise HTTPException(409, "Пользователь с таким email уже существует")

        # Проверяем, существует ли уже пользователь с таким username
        if self.repo.get_user_by_username(username):
            raise HTTPException(409, "Пользователь с таким именем уже существует")

        pwd_hash, salt = self._hash_password(password)
        return self.repo.create_user(username, email, pwd_hash, salt)

    def login(self, email: str, password: str) -> tuple:
        user = self.repo.get_user_by_email(email)
        if not user or not user.password_hash:
            raise HTTPException(401, "Неверные учетные данные")

        pwd_hash, _ = self._hash_password(password, user.salt)
        if pwd_hash != user.password_hash:
            raise HTTPException(401, "Неверные учетные данные")

        access_token, refresh_token = self._generate_tokens(user)
        return user, access_token, refresh_token

    def refresh(self, refresh_token: str) -> tuple:
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(401, "Невалидный refresh токен")

        token_record = self.repo.find_token_by_refresh_hash(hash_token(refresh_token))
        if not token_record:
            raise HTTPException(401, "Токен отозван или не существует")

        user = token_record.user
        if not user:
            raise HTTPException(401, "Пользователь не найден")

        # Отзываем старый токен
        self.repo.revoke_token(token_record)

        # Генерируем новые
        access_token, new_refresh_token = self._generate_tokens(user)
        return user, access_token, new_refresh_token

    def get_profile(self, user_id: str):
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(404, "Пользователь не найден")
        return user

    def logout(self, access_token: str):
        token_record = self.repo.find_token_by_access_hash(hash_token(access_token))
        if token_record:
            self.repo.revoke_token(token_record)

    def logout_all(self, user_id: str):
        self.repo.revoke_all_user_tokens(user_id)

    @staticmethod
    def get_yandex_auth_url(state: str) -> str:
        return f"https://oauth.yandex.ru/authorize?response_type=code&client_id={YANDEX_CLIENT_ID}&state={state}"

    def handle_yandex_callback(self, code: str) -> tuple:
        """Обменивает код на токен Яндекса и возвращает токены приложения"""
        try:
            # 1. Получаем токен от Яндекса
            token_url = "https://oauth.yandex.ru/token"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": YANDEX_CLIENT_ID,
                "client_secret": YANDEX_CLIENT_SECRET,
            }
            response = httpx.post(token_url, data=data)
            response.raise_for_status()
            access_token_yandex = response.json()["access_token"]

            # 2. Получаем инфу о юзере
            user_url = "https://login.yandex.ru/info"
            headers = {"Authorization": f"OAuth {access_token_yandex}"}
            user_response = httpx.get(user_url, headers=headers)
            user_response.raise_for_status()
            user_info = user_response.json()

            yandex_id = user_info["id"]
            email = user_info.get("default_email")
            username = user_info.get("login")

            # 3. Ищем или создаем юзера в нашей БД
            user = self.repo.get_user_by_yandex_id(yandex_id)
            if not user:
                # Если с таким email уже есть обычный аккаунт - ошибка
                if self.repo.get_user_by_email(email):
                    raise HTTPException(409, "Email уже занят другим аккаунтом")
                user = self.repo.create_oauth_user(username, email, yandex_id)

            access_token, refresh_token = self._generate_tokens(user)
            return user, access_token, refresh_token

        except httpx.HTTPError:
            raise HTTPException(400, "Ошибка при авторизации через Яндекс")

    def forgot_password(self, email: str) -> str:
        """Генерирует токен сброса (без реальной отправки на почту для лабы)"""
        user = self.repo.get_user_by_email(email)
        if not user:
            return ""  # Не выдаем, что юзера нет (в целях безопасности)

        # Для простоты лабораторной генерируем токен-заглушку
        reset_token = str(uuid.uuid4())
        # В реальном приложении этот токен сохранится в БД с временем жизни
        user.salt = reset_token  # Хак для лабы: храним токен в поле salt
        user.save()
        return reset_token

    def reset_password(self, token: str, new_password: str):
        # Находим юзера по токену (который мы временно засунули в salt)
        from app.models import User

        user = User.objects(salt=token, deleted_at=None).first()  # type: ignore

        if not user:
            raise HTTPException(400, "Неверный или просроченный токен")

        pwd_hash, new_salt = self._hash_password(new_password)
        self.repo.update_password(user, pwd_hash, new_salt)
