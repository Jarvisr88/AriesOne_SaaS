"""Base repository for database operations."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from fastapi import HTTPException, status

from ...domain.models.base import Base
from .database import DatabaseService
from ..cache import CacheService
from ..logging import get_logger
from ..metrics import MetricsService

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    """Base repository for common database operations."""

    def __init__(
        self,
        db: DatabaseService,
        model: Type[T],
        cache: Optional[CacheService] = None,
        metrics: Optional[MetricsService] = None
    ):
        """Initialize repository."""
        self.db = db
        self.model = model
        self.cache = cache
        self.metrics = metrics
        self.logger = get_logger(f"{__name__}.{model.__name__}Repository")

        # Cache settings
        self.cache_enabled = cache is not None
        self.cache_prefix = f"{model.__name__.lower()}:"
        self.cache_ttl = 300  # 5 minutes

    def _get_cache_key(self, id: Union[str, UUID]) -> str:
        """Get cache key for entity."""
        return f"{self.cache_prefix}{str(id)}"

    async def _cache_entity(self, entity: T) -> None:
        """Cache entity if caching is enabled."""
        if self.cache_enabled and entity:
            await self.cache.set(
                self._get_cache_key(entity.id),
                entity.to_dict(),
                self.cache_ttl
            )
            if self.metrics:
                self.metrics.increment(f"{self.model.__name__.lower()}.cache.set")

    async def _invalidate_cache(self, id: Union[str, UUID]) -> None:
        """Invalidate entity cache."""
        if self.cache_enabled:
            await self.cache.delete(self._get_cache_key(id))
            if self.metrics:
                self.metrics.increment(f"{self.model.__name__.lower()}.cache.invalidate")

    async def get_by_id(
        self,
        id: Union[str, UUID],
        *,
        use_cache: bool = True
    ) -> Optional[T]:
        """Get entity by ID."""
        try:
            # Check cache first
            if use_cache and self.cache_enabled:
                cached_data = await self.cache.get(self._get_cache_key(id))
                if cached_data:
                    if self.metrics:
                        self.metrics.increment(f"{self.model.__name__.lower()}.cache.hit")
                    return self.model(**cached_data)

            # Get from database
            async with self.db.session() as session:
                result = await session.get(self.model, id)
                if result:
                    await self._cache_entity(result)
                return result

        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} by ID: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.model.__name__.lower()}.error.get_by_id")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving {self.model.__name__}"
            )

    async def find_one(
        self,
        *conditions: Any,
        **filters: Any
    ) -> Optional[T]:
        """Find single entity by conditions."""
        try:
            query = select(self.model)
            if conditions:
                query = query.where(and_(*conditions))
            if filters:
                query = query.filter_by(**filters)

            async with self.db.session() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()

        except Exception as e:
            self.logger.error(f"Error finding {self.model.__name__}: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.model.__name__.lower()}.error.find_one")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error finding {self.model.__name__}"
            )

    async def find_many(
        self,
        *conditions: Any,
        offset: int = 0,
        limit: int = 100,
        **filters: Any
    ) -> List[T]:
        """Find multiple entities by conditions."""
        try:
            query = select(self.model)
            if conditions:
                query = query.where(and_(*conditions))
            if filters:
                query = query.filter_by(**filters)
            
            query = query.offset(offset).limit(limit)

            async with self.db.session() as session:
                result = await session.execute(query)
                return list(result.scalars().all())

        except Exception as e:
            self.logger.error(f"Error finding {self.model.__name__}s: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.model.__name__.lower()}.error.find_many")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error finding {self.model.__name__}s"
            )

    async def create(
        self,
        data: Dict[str, Any],
        *,
        session: Optional[AsyncSession] = None
    ) -> T:
        """Create new entity."""
        try:
            async with self.db.transaction(session) as session_ctx:
                instance = self.model(**data)
                session_ctx.add(instance)
                await session_ctx.flush()
                await session_ctx.refresh(instance)
                
                # Cache new entity
                await self._cache_entity(instance)
                
                if self.metrics:
                    self.metrics.increment(f"{self.model.__name__.lower()}.created")
                
                return instance

        except Exception as e:
            self.logger.error(f"Error creating {self.model.__name__}: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.model.__name__.lower()}.error.create")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating {self.model.__name__}"
            )

    async def update(
        self,
        id: Union[str, UUID],
        data: Dict[str, Any],
        *,
        session: Optional[AsyncSession] = None
    ) -> Optional[T]:
        """Update existing entity."""
        try:
            async with self.db.transaction(session) as session_ctx:
                instance = await session_ctx.get(self.model, id)
                if instance:
                    for key, value in data.items():
                        setattr(instance, key, value)
                    await session_ctx.flush()
                    await session_ctx.refresh(instance)
                    
                    # Update cache
                    await self._cache_entity(instance)
                    
                    if self.metrics:
                        self.metrics.increment(f"{self.model.__name__.lower()}.updated")
                    
                    return instance
                return None

        except Exception as e:
            self.logger.error(f"Error updating {self.model.__name__}: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.model.__name__.lower()}.error.update")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating {self.model.__name__}"
            )

    async def delete(
        self,
        id: Union[str, UUID],
        *,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """Delete entity by ID."""
        try:
            async with self.db.transaction(session) as session_ctx:
                instance = await session_ctx.get(self.model, id)
                if instance:
                    await session_ctx.delete(instance)
                    
                    # Invalidate cache
                    await self._invalidate_cache(id)
                    
                    if self.metrics:
                        self.metrics.increment(f"{self.model.__name__.lower()}.deleted")
                    
                    return True
                return False

        except Exception as e:
            self.logger.error(f"Error deleting {self.model.__name__}: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.model.__name__.lower()}.error.delete")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting {self.model.__name__}"
            )

    async def count(
        self,
        *conditions: Any,
        **filters: Any
    ) -> int:
        """Count entities matching conditions."""
        try:
            query = select(self.model)
            if conditions:
                query = query.where(and_(*conditions))
            if filters:
                query = query.filter_by(**filters)

            async with self.db.session() as session:
                result = await session.execute(query)
                return len(result.scalars().all())

        except Exception as e:
            self.logger.error(f"Error counting {self.model.__name__}s: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.model.__name__.lower()}.error.count")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error counting {self.model.__name__}s"
            )

    def build_query(self) -> Select:
        """Build base query for model."""
        return select(self.model)
