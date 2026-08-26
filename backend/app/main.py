from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine


app = FastAPI(
    title="RepoLens API",
    description="AI-powered codebase intelligence assistant",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "repolens-api"
    }


@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            value = result.scalar()

        return {
            "database": "connected",
            "result": value
        }
    except Exception as e:
        return {
            "database": "disconnected",
            "error": str(e)
        }