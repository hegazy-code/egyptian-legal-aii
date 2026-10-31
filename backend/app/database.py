"""
SQLAlchemy engine / session setup.

Works against the DATABASE_URL in app/config.py. Defaults to SQLite for
zero-dependency local development; swapping DATABASE_URL to a Postgres DSN
later requires no changes here since create_engine() dispatches on the URL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # Needed for SQLite when used with FastAPI's threaded request handling.
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
