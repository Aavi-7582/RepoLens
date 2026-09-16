from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine, Base
from app.core.config import settings
from app.api.repositories import router as repository_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging_config import setup_logging

setup_logging()

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()

    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="RepoLens API",
    description="AI-powered codebase intelligence assistant",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(repository_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "database": "connected",
        "result": value
    }