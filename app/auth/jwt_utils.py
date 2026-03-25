import base64
import hashlib
import hmac
import json
import os
import time

from app.config import (
    JWT_ACCESS_EXPIRATION,
    JWT_ACCESS_SECRET,
    JWT_REFRESH_EXPIRATION,
    JWT_REFRESH_SECRET,
)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def _sign(payload_str: str, secret: str) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(payload_str.encode())
    sig = hmac.new(
        secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256
    ).digest()
    return f"{header}.{payload}.{_b64url_encode(sig)}"


def create_access_token(user_id: int) -> str:
    payload = json.dumps(
        {
            "sub": user_id,
            "type": "access",
            "exp": int(time.time()) + JWT_ACCESS_EXPIRATION * 60,
        }
    )
    return _sign(payload, JWT_ACCESS_SECRET)


def create_refresh_token(user_id: int) -> str:
    payload = json.dumps(
        {
            "sub": user_id,
            "type": "refresh",
            "exp": int(time.time()) + JWT_REFRESH_EXPIRATION * 60,
            "jti": os.urandom(16).hex(),
        }
    )
    return _sign(payload, JWT_REFRESH_SECRET)


def _verify(token: str, secret: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_payload = f"{parts[0]}.{parts[1]}"
        sig = hmac.new(
            secret.encode(), header_payload.encode(), hashlib.sha256
        ).digest()
        if _b64url_encode(sig) != parts[2]:
            return None
        payload = json.loads(_b64url_decode(parts[1]))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def verify_access_token(token: str) -> dict | None:
    return _verify(token, JWT_ACCESS_SECRET)


def verify_refresh_token(token: str) -> dict | None:
    return _verify(token, JWT_REFRESH_SECRET)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
