from fastapi import FastAPI
from mongoengine import connect

from app.auth.router import router as auth_router
from app.config import ENVIRONMENT, MONGO_URI
from app.router import router as users_router
from app.storage.router import router as files_router

app = FastAPI(title="User API Mongo")


@app.on_event("startup")
def startup_db():
    connect(host=MONGO_URI)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(files_router)


@app.get("/")
def health():
    return {"status": "ok", "db": "mongodb"}
