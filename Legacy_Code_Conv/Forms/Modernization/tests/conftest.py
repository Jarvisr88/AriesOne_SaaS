"""Test configuration and fixtures.

This module provides pytest fixtures for testing.
"""
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from core.db.base import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost/test_db",
        echo=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
