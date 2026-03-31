from fastapi import FastAPI
from sqlalchemy import inspect

from app.api.auth import router as auth_router
from app.api.boo import router as boo_router
from app.api.meals import router as meals_router
from app.api.quiz import router as quiz_router
from app.api.users import router as users_router
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.seed import seed_initial_data

app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(quiz_router)
app.include_router(meals_router)
app.include_router(boo_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    with engine.connect() as connection:
        has_users_table = inspect(connection).has_table("users")

    if not has_users_table:
        return

    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
