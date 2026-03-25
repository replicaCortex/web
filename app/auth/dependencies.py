from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.jwt_utils import hash_token, verify_access_token
from app.auth.repository import AuthRepository
from app.database import get_db


def get_current_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db),
) -> dict:
    if not access_token:
        raise HTTPException(401, "Не авторизован")
    payload = verify_access_token(access_token)
    if not payload:
        raise HTTPException(401, "Токен истёк или невалиден")
    # Проверяем, не отозван ли
    repo = AuthRepository(db)
    record = repo.find_token_by_access_hash(hash_token(access_token))
    if not record:
        raise HTTPException(401, "Токен отозван")
    return {"user_id": payload["sub"], "access_token": access_token}
