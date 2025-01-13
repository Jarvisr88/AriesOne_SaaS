"""Database configuration module."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800
    ECHO_SQL: bool = False

    @property
    def database_url(self) -> str:
        """Get the database URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"

class Database:
    """Database connection manager."""

    def __init__(self, settings: Optional[DatabaseSettings] = None):
        """Initialize database connection manager.
        
        Args:
            settings: Database settings. If None, loads from environment.
        """
        self.settings = settings or DatabaseSettings()
        self.engine = create_async_engine(
            self.settings.database_url,
            echo=self.settings.ECHO_SQL,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=self.settings.POOL_SIZE,
            max_overflow=self.settings.MAX_OVERFLOW,
            pool_timeout=self.settings.POOL_TIMEOUT,
            pool_recycle=self.settings.POOL_RECYCLE
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        """Get a database session.
        
        Returns:
            AsyncSession: Database session.
        """
        async with self.async_session() as session:
            yield session

db = Database()
get_session = db.get_session
