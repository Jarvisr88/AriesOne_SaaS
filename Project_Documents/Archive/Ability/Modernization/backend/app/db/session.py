from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create async PostgreSQL engine
engine = create_async_engine(
    settings.POSTGRES_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.DB_ECHO_SQL
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Async session dependency
async_session = AsyncSessionLocal
