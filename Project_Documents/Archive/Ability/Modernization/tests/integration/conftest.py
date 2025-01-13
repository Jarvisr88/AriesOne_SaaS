import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.main import app
from app.services.redis_client import RedisClient

@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()

@pytest.fixture(scope="session")
def client() -> Generator:
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def redis_client() -> Generator:
    client = RedisClient(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_TEST_DB
    )
    yield client
    # Clear test database after tests
    client.flushdb()

@pytest.fixture(autouse=True)
def clear_cache(redis_client):
    """Clear Redis cache before each test"""
    redis_client.flushdb()

@pytest.fixture(autouse=True)
def clear_rate_limits(redis_client):
    """Clear rate limit data before each test"""
    keys = redis_client.keys("rate_limit:*")
    if keys:
        redis_client.delete(*keys)

@pytest.fixture
def db_session(db: Session) -> Generator:
    """Returns a database session for each test"""
    try:
        yield db
    finally:
        db.rollback()

@pytest.fixture(autouse=True)
def setup_test_db(db_session: Session):
    """Set up test database before each test"""
    # Create required tables
    from app.db.base import Base
    Base.metadata.create_all(bind=db_session.get_bind())
    yield
    # Clean up after test
    Base.metadata.drop_all(bind=db_session.get_bind())
