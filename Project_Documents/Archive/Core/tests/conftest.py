"""
Test configuration and fixtures for integration tests.
"""
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Generator

from ..database import Base, get_db
from ..main import app
from ..config import settings

# Create async test engine
test_engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=True,
    future=True
)

# Create async session for tests
async_session = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database and tables"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Get database session for tests"""
    async with async_session() as session:
        yield session

@pytest.fixture
async def client(db_session) -> Generator:
    """Get test client"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
