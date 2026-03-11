from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    from app.database import engine

    await engine.dispose()


app = FastAPI(
    title=settings.APP_TITLE,
    description="REST API для управления пользователями",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(router)


@app.get(
    "/",
    summary="Healthcheck",
    description="Проверка работоспособности API",
)
async def root():
    return {
        "status": "ok",
        "app": settings.APP_TITLE,
        "version": "1.0.0",
    }
