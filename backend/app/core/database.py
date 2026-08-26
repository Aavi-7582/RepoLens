from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Relative import prevents ModuleNotFoundError when running uvicorn
from .config import settings

# Force 127.0.0.1 to avoid Windows IPv6 (::1) lookup errors with Docker
db_url = settings.database_url.replace("localhost", "127.0.0.1")

engine = create_engine(db_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()