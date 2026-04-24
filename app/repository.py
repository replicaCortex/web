from datetime import datetime

from app.models import User


class UserRepository:
    def _active(self):
        return User.objects(deleted_at=None)

    def create(self, data):
        user = User(**data.model_dump())
        user.save()
        return user

    def get_by_id(self, user_id: str):
        return self._active().filter(id=user_id).first()

    def get_all(self, offset: int, limit: int):
        query = self._active()
        total = query.count()
        users = query.skip(offset).limit(limit)
        return list(users), total

    def update_full(self, user, data):
        user.update(**data.model_dump())
        user.reload()
        return user

    def update_partial(self, user, data):
        user.update(**data.model_dump(exclude_unset=True))
        user.reload()
        return user

    def soft_delete(self, user):
        user.update(deleted_at=datetime.utcnow())
