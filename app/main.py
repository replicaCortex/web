from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.exceptions import register_exception_handlers
from app.routers import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    from app.database import engine

    await engine.dispose()


app = FastAPI(
    title=settings.APP_TITLE,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(user_router)


@app.get("/", summary="Healthcheck")
async def root():
    return {"status": "ok", "app": settings.APP_TITLE}
