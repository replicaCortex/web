from fastapi import FastAPI

from app.config import ENVIRONMENT
from app.router import router

app = FastAPI(
    title="User API",
    version="1.0.1",
    description="REST API для управления пользователями",
    contact={
        "name": "replica",
        "email": "replicaCortex@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
)

app.include_router(router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok"}


if ENVIRONMENT == "production":
    app.docs_url = None
    app.redoc_url = None
