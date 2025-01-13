"""
Database abstraction layer for AriesOne SaaS platform.
Provides a unified interface for database operations using SQLAlchemy and AsyncPG.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Type variable for ORM models
T = TypeVar('T')

# Base class for all ORM models
Base = declarative_base()

class DatabaseConfig:
    """Configuration settings for database connections."""
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        min_pool_size: int = 10,
        max_pool_size: int = 100,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
        echo: bool = False
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo

    @property
    def connection_url(self) -> str:
        """Generate SQLAlchemy connection URL."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

class Database:
    """Core database interface providing connection management and CRUD operations."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_async_engine(
            config.connection_url,
            poolclass=AsyncAdaptedQueuePool,
            pool_pre_ping=True,
            pool_size=config.max_pool_size,
            max_overflow=config.max_pool_size - config.min_pool_size,
            pool_timeout=config.pool_timeout,
            pool_recycle=config.pool_recycle,
            echo=config.echo
        )
        self.async_session = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        self.logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """Create a new database session with automatic cleanup."""
        session = self.async_session()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()

    async def health_check(self) -> bool:
        """Verify database connection is healthy."""
        try:
            async with self.session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

class Repository:
    """Base repository class implementing common CRUD operations."""
    
    def __init__(self, db: Database, model: Type[T]):
        self.db = db
        self.model = model
        self.logger = logging.getLogger(__name__)

    async def create(self, **kwargs) -> T:
        """Create a new record."""
        async with self.db.session() as session:
            try:
                instance = self.model(**kwargs)
                session.add(instance)
                await session.commit()
                return instance
            except Exception as e:
                self.logger.error(f"Create operation failed: {str(e)}")
                raise

    async def get(self, id: Any) -> Optional[T]:
        """Retrieve a record by ID."""
        async with self.db.session() as session:
            try:
                return await session.get(self.model, id)
            except Exception as e:
                self.logger.error(f"Get operation failed: {str(e)}")
                raise

    async def update(self, id: Any, **kwargs) -> Optional[T]:
        """Update a record by ID."""
        async with self.db.session() as session:
            try:
                instance = await session.get(self.model, id)
                if instance:
                    for key, value in kwargs.items():
                        setattr(instance, key, value)
                    await session.commit()
                return instance
            except Exception as e:
                self.logger.error(f"Update operation failed: {str(e)}")
                raise

    async def delete(self, id: Any) -> bool:
        """Delete a record by ID."""
        async with self.db.session() as session:
            try:
                instance = await session.get(self.model, id)
                if instance:
                    await session.delete(instance)
                    await session.commit()
                    return True
                return False
            except Exception as e:
                self.logger.error(f"Delete operation failed: {str(e)}")
                raise

    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List records with pagination."""
        async with self.db.session() as session:
            try:
                query = await session.execute(
                    self.model.__table__.select()
                    .offset(skip)
                    .limit(limit)
                )
                return query.scalars().all()
            except Exception as e:
                self.logger.error(f"List operation failed: {str(e)}")
                raise
