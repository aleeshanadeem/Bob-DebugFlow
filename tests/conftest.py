"""
tests/conftest.py
-----------------
Shared pytest fixtures for the Bob DebugFlow test suite.

Sets up an in-memory SQLite database for each test session so that:
  - Tests are fully isolated from each other (no shared state).
  - No file-system artefacts are created during test runs.
  - Tests run fast — no disk I/O for the database.

The fixture overrides the app's SQLAlchemy engine and get_db dependency
before any routes are invoked.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# In-memory SQLite URL — every test session gets a fresh empty database.
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def db_engine():
    """Create a single in-memory engine shared across the test session."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Provide a transactional database session per test function.

    Each test runs inside a transaction that is rolled back after the test
    completes, ensuring full isolation without recreating the schema.
    """
    connection = db_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=connection
    )
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Provide a FastAPI TestClient with the database dependency overridden
    to use the isolated in-memory session from db_session.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
