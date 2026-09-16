from sqlalchemy import text
from app.core.database import engine, Base
from app.models import Repository, RepositoryFile
from app.models.chunk import CodeChunk

print("=== Testing DB Connection and Tables ===")

with engine.connect() as conn:
    # Check tables
    result = conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
    ))
    tables = [r[0] for r in result.fetchall()]
    print("Existing tables:", tables)

    # Check vector extension
    result2 = conn.execute(text("SELECT extname, extversion FROM pg_extension WHERE extname='vector'"))
    ext = result2.fetchall()
    print("pgvector extension:", ext)

# Try creating tables
print("\n=== Creating tables if not exist ===")
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()

Base.metadata.create_all(bind=engine)

with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
    ))
    tables = [r[0] for r in result.fetchall()]
    print("Tables after create_all:", tables)

print("\nAll done!")
