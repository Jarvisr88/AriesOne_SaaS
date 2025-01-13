"""Core database module for AriesOne SaaS platform."""

from typing import Any, AsyncGenerator, Dict, List, Optional, Type, TypeVar
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import Select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from .database_config import DatabaseSettings, get_database_settings
from ..logging import get_logger
from ..metrics import MetricsService
from ..cache import CacheService, get_cache_service
from ...domain.models.base import Base

T = TypeVar("T", bound=Base)

class DatabaseService:
    """Database service for managing database operations."""

    def __init__(
        self,
        settings: DatabaseSettings,
        cache: CacheService,
        metrics: MetricsService,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize database service."""
        self.settings = settings
        self.cache = cache
        self.metrics = metrics
        self.logger = logger or get_logger(__name__)
        
        # Create async engine
        self.engine = create_async_engine(
            settings.database_url,
            **settings.get_pool_settings()
        )
        
        # Create session factory
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def initialize(self) -> None:
        """Initialize database and create tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def shutdown(self) -> None:
        """Shutdown database connections."""
        await self.engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        session: AsyncSession = self.async_session_maker()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def execute_query(
        self,
        query: Select,
        *,
        session: Optional[AsyncSession] = None,
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None
    ) -> List[Any]:
        """Execute a database query with optional caching."""
        # Check cache if cache_key provided
        if cache_key:
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                self.metrics.increment("database.cache.hit")
                return cached_result

        start_time = datetime.now()
        
        try:
            async with self.session() as session_ctx:
                session_to_use = session or session_ctx
                result = await session_to_use.execute(query)
                data = result.scalars().all()

                # Cache result if cache_key provided
                if cache_key and data:
                    await self.cache.set(
                        cache_key,
                        data,
                        cache_ttl or self.settings.CACHE_TTL
                    )
                    self.metrics.increment("database.cache.set")

                # Record metrics
                execution_time = (datetime.now() - start_time).total_seconds()
                self.metrics.timing("database.query.execution_time", execution_time)
                self.metrics.increment("database.query.success")

                return data

        except SQLAlchemyError as e:
            self.logger.error(f"Database query error: {str(e)}", exc_info=True)
            self.metrics.increment("database.query.error")
            raise

    @asynccontextmanager
    async def transaction(
        self,
        session: Optional[AsyncSession] = None
    ) -> AsyncGenerator[AsyncSession, None]:
        """Execute operations in a transaction."""
        async with self.session() as session_ctx:
            session_to_use = session or session_ctx
            try:
                async with session_to_use.begin():
                    yield session_to_use
            except Exception as e:
                self.logger.error(f"Transaction error: {str(e)}", exc_info=True)
                self.metrics.increment("database.transaction.error")
                raise

    async def get_by_id(
        self,
        model: Type[T],
        id: Any,
        *,
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None
    ) -> Optional[T]:
        """Get entity by ID with optional caching."""
        if cache_key:
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                self.metrics.increment("database.cache.hit")
                return cached_result

        async with self.session() as session:
            result = await session.get(model, id)
            if result and cache_key:
                await self.cache.set(
                    cache_key,
                    result,
                    cache_ttl or self.settings.CACHE_TTL
                )
                self.metrics.increment("database.cache.set")
            return result

    async def create(
        self,
        model: Type[T],
        data: Dict[str, Any],
        *,
        session: Optional[AsyncSession] = None
    ) -> T:
        """Create a new entity."""
        async with self.transaction(session) as session_ctx:
            instance = model(**data)
            session_ctx.add(instance)
            await session_ctx.flush()
            await session_ctx.refresh(instance)
            return instance

    async def update(
        self,
        model: Type[T],
        id: Any,
        data: Dict[str, Any],
        *,
        session: Optional[AsyncSession] = None
    ) -> Optional[T]:
        """Update an existing entity."""
        async with self.transaction(session) as session_ctx:
            instance = await session_ctx.get(model, id)
            if instance:
                for key, value in data.items():
                    setattr(instance, key, value)
                await session_ctx.flush()
                await session_ctx.refresh(instance)
            return instance

    async def delete(
        self,
        model: Type[T],
        id: Any,
        *,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """Delete an entity."""
        async with self.transaction(session) as session_ctx:
            instance = await session_ctx.get(model, id)
            if instance:
                await session_ctx.delete(instance)
                return True
            return False

    async def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            async with self.session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}", exc_info=True)
            return False


# Dependency injection
async def get_db_service(
    settings: DatabaseSettings = Depends(get_database_settings),
    cache: CacheService = Depends(get_cache_service),
    metrics: MetricsService = Depends()
) -> DatabaseService:
    """Get database service instance."""
    return DatabaseService(settings, cache, metrics)
