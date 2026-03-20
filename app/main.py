from fastapi import FastAPI

from app.router import router

app = FastAPI(title="User API", version="1.0.0")

app.include_router(router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok"}
