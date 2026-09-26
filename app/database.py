"""
app/database.py
---------------
Database engine and session management for the Bob DebugFlow sample app.

Uses SQLite for zero-infrastructure local development and testing.
The get_db() dependency is injected into route handlers via FastAPI's
Depends() mechanism.

NOTE: This module contains an intentional bug (B6) related to session
lifecycle management in error paths.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite file-based database for the running app.
# Tests override this via the conftest fixture.
DATABASE_URL = "sqlite:///./debugflow.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base class shared by all ORM models."""
    pass


def get_db():
    """
    FastAPI dependency that yields a database session.

    The session is closed in a finally block so it is always released,
    whether the request succeeds or raises an exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
