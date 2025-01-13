"""Test configuration and fixtures."""
import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from infrastructure.database.base import Base
from api.main import app
from api.dependencies import get_db

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
def test_client(test_session: AsyncSession) -> Generator:
    """Create test client."""
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers() -> dict:
    """Create auth headers for tests."""
    return {
        "Authorization": "Bearer test_token"
    }
