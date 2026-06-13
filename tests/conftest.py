import os
import uuid

os.environ["DB_USERNAME"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_DATABASE"] = "test_db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from tasks_router.dependencies import get_db
from tasks_router.main import app
from tasks_router.models.base_model import Base


@pytest.fixture(scope="session")
def db_engine():
    """
    Creates a single database engine for the entire test session.
    Uses an in-memory SQLite database with StaticPool to keep the same database
    across multiple connections.
    """
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """
    Provides a transactional database session for a single test.
    Rolls back all changes at the end of the test.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session_local = sessionmaker(
        bind=connection,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    session = session_local()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    """
    Provides a FastAPI TestClient with get_db overridden to use the 
    transactional db_session.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def user_payload():
    return {
        "id": str(uuid.uuid4()),
        "username": "alice",
        "display_name": "Alice Example",
    }
