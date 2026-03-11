# test_repository.py (временный файл для проверки)

import asyncio

from app.database import async_session_factory
from app.repositories import UserRepository
from app.schemas import UserCreate, UserUpdate


async def test():
    async with async_session_factory() as session:
        repo = UserRepository(session)

        # Создаём пользователя
        user = await repo.create(
            UserCreate(
                username="foo",
                email="replicaCortex@foobar.com",
                os="linux",
                totaltime=10,
            )
        )
        # Читаем по ID
        found = await repo.get_by_id(user.id)
        print(f"✅ Найден по ID: {found}")

        # Читаем по username
        found2 = await repo.get_by_username("foo")
        print(f"✅ Найден по username: {found2}")

        # Обновляем
        updated = await repo.update(
            user.id,
            UserUpdate(email="replicaCortex@foobar.com"),
        )
        print(f"✅ Обновлён: email={updated.email}")

        # Список всех
        all_users = await repo.get_all()
        print(f"✅ Всего пользователей: {len(all_users)}")

        # Удаляем
        deleted = await repo.delete(user.id)
        print(f"✅ Удалён: {deleted}")

        # Проверяем, что удалён
        gone = await repo.get_by_id(user.id)
        print(f"✅ После удаления: {gone}")


asyncio.run(test())
