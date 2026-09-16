"""
Test to identify Supabase-specific issues with the current setup.
"""
from sqlalchemy import text, event
from sqlalchemy import create_engine
import os, sys

# Load the URL
sys.path.insert(0, '.')
from app.core.config import settings

db_url = settings.database_url
print(f"URL (masked): {db_url[:60]}...")
print(f"Port: {db_url.split(':')[3].split('/')[0] if ':' in db_url else 'N/A'}")

print("\n--- Test 1: Basic connection ---")
engine = create_engine(db_url, connect_args={"sslmode": "require"}, pool_pre_ping=True)
with engine.connect() as conn:
    r = conn.execute(text("SELECT version()"))
    print("PG version:", r.scalar()[:60])

print("\n--- Test 2: CREATE EXTENSION (transaction pooler compatible?) ---")
try:
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    print("OK")
except Exception as e:
    print("ERROR:", e)

print("\n--- Test 3: Check search_path ---")
with engine.connect() as conn:
    r = conn.execute(text("SHOW search_path"))
    print("search_path:", r.scalar())

print("\n--- Test 4: Check vector schema ---")
with engine.connect() as conn:
    r = conn.execute(text(
        "SELECT nspname FROM pg_catalog.pg_namespace n "
        "JOIN pg_catalog.pg_extension e ON e.extnamespace = n.oid "
        "WHERE e.extname = 'vector'"
    ))
    print("vector extension schema:", r.scalar())

print("\n--- Test 5: Table DDL with create_all ---")
from app.core.database import Base, engine as app_engine
from app.models import Repository, RepositoryFile
from app.models.chunk import CodeChunk
try:
    Base.metadata.create_all(bind=app_engine)
    print("create_all OK")
except Exception as e:
    print("create_all ERROR:", e)

print("\nDone.")
