"""Database connection and session management.

This module provides the core database functionality including:
- Async engine creation
- Session management
- Connection pooling
- Health checks
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.pool import AsyncAdaptedQueuePool

from .config import get_database_settings

# Get database settings
settings = get_database_settings()

# Create async engine with connection pooling
engine = create_async_engine(
    settings.async_database_url,
    poolclass=AsyncAdaptedQueuePool,
    **settings.pool_args,
    echo=False  # Set to True for SQL logging
)

# Create async session factory
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session.
    
    Provides a context manager for database sessions with automatic
    cleanup and rollback on errors.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        ```python
        async with get_session() as session:
            result = await session.execute(query)
            await session.commit()
        ```
    """
    session = AsyncSessionFactory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def check_database_connection() -> bool:
    """Check database connection health.
    
    Returns:
        bool: True if connection is healthy, False otherwise
        
    Example:
        ```python
        is_healthy = await check_database_connection()
        if not is_healthy:
            logger.error("Database connection failed")
        ```
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


async def get_connection_stats() -> dict:
    """Get connection pool statistics.
    
    Returns:
        dict: Pool statistics including:
            - size: Current pool size
            - checked_out: Number of connections in use
            - overflow: Number of overflow connections
            - checkedin: Number of checked in connections
            
    Example:
        ```python
        stats = await get_connection_stats()
        print(f"Pool size: {stats['size']}")
        print(f"In use: {stats['checked_out']}")
        ```
    """
    return {
        "size": engine.pool.size(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "checkedin": engine.pool.checkedin()
    }


async def cleanup_pool() -> None:
    """Cleanup connection pool.
    
    Disposes of the engine and all connections in the pool.
    Should be called during application shutdown.
    
    Example:
        ```python
        @app.on_event("shutdown")
        async def shutdown():
            await cleanup_pool()
        ```
    """
    await engine.dispose()
