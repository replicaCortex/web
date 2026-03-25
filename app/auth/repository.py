from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import JWT_REFRESH_EXPIRATION
from app.models import TokenRecord, User


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- User ---
    def get_user_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email, User.deleted_at.is_(None))
            .first()
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        return (
            self.db.query(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )

    def get_user_by_yandex_id(self, yandex_id: str) -> User | None:
        return self.db.query(User).filter(User.yandex_id == yandex_id).first()

    def create_user(
        self, username: str, email: str, password_hash: str, salt: str
    ) -> User:
        user = User(
            username=username, email=email, password_hash=password_hash, salt=salt
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_oauth_user(self, username: str, email: str, yandex_id: str) -> User:
        user = User(username=username, email=email, yandex_id=yandex_id, os="unknown")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, password_hash: str, salt: str):
        user.password_hash = password_hash
        user.salt = salt
        self.db.commit()

    # --- Tokens ---
    def save_token(self, user_id: int, access_hash: str, refresh_hash: str):
        record = TokenRecord(
            user_id=user_id,
            access_token_hash=access_hash,
            refresh_token_hash=refresh_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=JWT_REFRESH_EXPIRATION),
        )
        self.db.add(record)
        self.db.commit()

    def find_token_by_refresh_hash(self, refresh_hash: str) -> TokenRecord | None:
        return (
            self.db.query(TokenRecord)
            .filter(
                TokenRecord.refresh_token_hash == refresh_hash,
                TokenRecord.revoked == False,
            )
            .first()
        )

    def find_token_by_access_hash(self, access_hash: str) -> TokenRecord | None:
        return (
            self.db.query(TokenRecord)
            .filter(
                TokenRecord.access_token_hash == access_hash,
                TokenRecord.revoked == False,
            )
            .first()
        )

    def revoke_token(self, record: TokenRecord):
        record.revoked = True
        self.db.commit()

    def revoke_all_user_tokens(self, user_id: int):
        self.db.query(TokenRecord).filter(
            TokenRecord.user_id == user_id,
            TokenRecord.revoked == False,
        ).update({"revoked": True})
        self.db.commit()
