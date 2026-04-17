import hashlib
import time
import uuid

import jwt

from app.config import (
    JWT_ACCESS_EXPIRATION,
    JWT_ACCESS_SECRET,
    JWT_REFRESH_EXPIRATION,
    JWT_REFRESH_SECRET,
)


def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": int(time.time()) + JWT_REFRESH_EXPIRATION * 60,
    }
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm="HS256")


def verify_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_ACCESS_SECRET, algorithms=["HS256"])
    except Exception:
        return None


def verify_refresh_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_REFRESH_SECRET, algorithms=["HS256"])
    except Exception:
        return None


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: int) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "type": "access",
        "exp": int(time.time()) + JWT_ACCESS_EXPIRATION * 60,
    }
    token = jwt.encode(payload, JWT_ACCESS_SECRET, algorithm="HS256")
    return token, jti
