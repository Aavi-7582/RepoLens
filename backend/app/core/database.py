from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

db_url = settings.database_url

# Handle Supabase connection string adjustments if necessary
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Create engine with SSL parameters for remote Supabase DB
engine = create_engine(
    db_url,
    connect_args={
        "sslmode": "require"
    },
    pool_pre_ping=True  # Automatically reconnect if connection drops
)

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