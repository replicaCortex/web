from fastapi import Cookie, Depends, HTTPException
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session

from app.auth.jwt_utils import hash_token, verify_access_token
from app.auth.repository import AuthRepository
from app.database import get_db

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


def get_current_user(
    token_from_swagger: str = Depends(cookie_scheme),
    access_token: str = Cookie(None),
    db: Session = Depends(get_db),
) -> dict:

    actual_token = access_token or token_from_swagger

    if not actual_token:
        raise HTTPException(401, "Не авторизован")

    payload = verify_access_token(actual_token)
    if not payload:
        raise HTTPException(401, "Токен истёк или невалиден")

    repo = AuthRepository(db)
    record = repo.find_token_by_access_hash(hash_token(actual_token))
    if not record:
        raise HTTPException(401, "Токен отозван")

    return {"user_id": int(payload["sub"]), "access_token": actual_token}
