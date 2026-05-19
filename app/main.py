from fastapi import FastAPI, HTTPException
from mongoengine import connect
from mongoengine.connection import get_connection

from app.auth.router import router as auth_router
from app.cache import cache_service
from app.config import MONGO_URI
from app.router import profile_router
from app.router import router as users_router
from app.storage.router import router as files_router

app = FastAPI(title="User API Mongo")


@app.get("/health/live", tags=["Health"])
def health_live():
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
def health_ready():
    try:
        cache_service.client.ping()
        get_connection().admin.command("ping")
        return {"status": "ready"}
    except Exception as e:
        print(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Dependencies not ready")


@app.on_event("startup")
def startup_db():
    connect(host=MONGO_URI)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(files_router)
app.include_router(profile_router)


@app.get("/")
def health():
    return {"status": "ok", "db": "mongodb"}
