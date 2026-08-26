from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine, Base
from app.models import Repository, RepositoryFile
from app.api.repositories import router as repository_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="RepoLens API",
    description="AI-powered codebase intelligence assistant",
    version="0.1.0"
)


app.include_router(repository_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "repolens-api"
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