"""
Test Configuration
Version: 1.0.0
Last Updated: 2025-01-10
"""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/test_db"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Create database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session."""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Mock settings for tests."""
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("EVENT_STORE_URL", "localhost")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "http://localhost/slack")
    monkeypatch.setenv("ALERT_WEBHOOK_URL", "http://localhost/alerts")
