"""Test configuration and fixtures."""
import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from infrastructure.config import get_database_settings
from models.base import Base


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    settings = get_database_settings()
    
    # Use test database
    test_db_url = settings.async_database_url.replace(
        settings.POSTGRES_DB,
        f"{settings.POSTGRES_DB}_test"
    )
    
    engine = create_async_engine(test_db_url, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_encryption_key() -> bytes:
    """Get test encryption key."""
    return b"test_key_32_bytes_long_for_testing"
