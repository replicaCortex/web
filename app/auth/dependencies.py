from fastapi import Cookie, Depends, HTTPException
from fastapi.security import APIKeyCookie

from app.auth.jwt_utils import hash_token, verify_access_token
from app.auth.repository import AuthRepository
from app.cache import cache_service

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


def get_current_user(
    token_from_swagger: str = Depends(cookie_scheme), access_token: str = Cookie(None)
) -> dict:
    actual_token = access_token or token_from_swagger
    if not actual_token:
        raise HTTPException(401, "Не авторизован")

    payload = verify_access_token(actual_token)
    if not payload:
        raise HTTPException(401, "Токен невалиден")

    repo = AuthRepository()
    record = repo.find_token_by_access_hash(hash_token(actual_token))
    if not record:
        raise HTTPException(401, "Токен отозван")

    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not cache_service.get(f"wp:auth:user:{user_id}:access:{jti}"):
        raise HTTPException(401, "Сессия истекла")

    return {"user_id": user_id, "access_token": actual_token}
