"""
SQLAlchemy engine + session setup.

Uses `settings.database_url`, which defaults to a local SQLite file so the
project runs with zero external setup. Moving to PostgreSQL later is a
one-line change in `.env` (DATABASE_URL=postgresql+psycopg2://...) plus
`pip install psycopg2-binary` — no code here needs to change.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# `check_same_thread` is only needed for SQLite (FastAPI handles requests
# on different threads); it's ignored by other database backends.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
