from datetime import datetime, timedelta, timezone

from app.config import JWT_REFRESH_EXPIRATION
from app.models import TokenRecord, User


class AuthRepository:
    def get_user_by_email(self, email: str):
        return User.objects(email=email, deleted_at=None).first()

    def get_user_by_id(self, user_id: str):
        return User.objects(id=user_id, deleted_at=None).first()

    def get_user_by_yandex_id(self, yandex_id: str):
        return User.objects(yandex_id=yandex_id).first()

    def create_user(self, username, email, password_hash, salt):
        user = User(
            username=username, email=email, password_hash=password_hash, salt=salt
        )
        user.save()
        return user

    def create_oauth_user(self, username, email, yandex_id):
        user = User(username=username, email=email, yandex_id=yandex_id)
        user.save()
        return user

    def update_password(self, user, password_hash, salt):
        user.update(
            password_hash=password_hash, salt=salt, updated_at=datetime.utcnow()
        )

    def save_token(self, user_id, access_hash, refresh_hash):
        record = TokenRecord(
            user=user_id,
            access_token_hash=access_hash,
            refresh_token_hash=refresh_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=JWT_REFRESH_EXPIRATION),
        )
        record.save()

    def find_token_by_refresh_hash(self, refresh_hash: str):
        return TokenRecord.objects(
            refresh_token_hash=refresh_hash, revoked=False
        ).first()

    def find_token_by_access_hash(self, access_hash: str):
        return TokenRecord.objects(access_token_hash=access_hash, revoked=False).first()

    def revoke_token(self, record):
        record.update(revoked=True)

    def revoke_all_user_tokens(self, user_id):
        TokenRecord.objects(user=user_id, revoked=False).update(revoked=True)
