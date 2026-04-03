from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.config import ENVIRONMENT
from app.router import router as users_router

if ENVIRONMENT == "production":
    app = FastAPI(
        title="User API",
        version="2.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
else:
    app = FastAPI(
        title="User API",
        version="2.0.0",
        description=(
            "REST API для управления пользователями.\n\n"
            "## Авторизация\n"
            "Токены передаются через **HttpOnly cookies**.\n"
            "Для тестирования: сначала вызовите `/auth/login`, "
            "после чего браузер автоматически отправляет cookies со всеми запросами.\n\n"
            "## Модули\n"
            "- **Auth** — регистрация, вход, OAuth, управление сессиями\n"
            "- **Users** — CRUD операции (требуют авторизации)\n"
        ),
        contact={"name": "replica", "email": "replicaCortex@gmail.com"},
        license_info={"name": "MIT"},
    )

app.include_router(auth_router)
app.include_router(users_router)


@app.get(
    "/",
    tags=["Health"],
    summary="Проверка работоспособности",
    responses={200: {"content": {"application/json": {"example": {"status": "ok"}}}}},
)
def health():
    return {"status": "ok"}
