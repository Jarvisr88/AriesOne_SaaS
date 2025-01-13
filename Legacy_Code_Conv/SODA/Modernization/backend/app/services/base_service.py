"""Base service for business logic operations."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from fastapi import HTTPException, status

from ..core.database.base_repository import BaseRepository
from ..core.logging import get_logger
from ..core.metrics import MetricsService
from ..domain.models.base import Base

T = TypeVar("T", bound=Base)

class BaseService(Generic[T]):
    """Base service for common business logic operations."""

    def __init__(
        self,
        repository: BaseRepository[T],
        metrics: Optional[MetricsService] = None
    ):
        """Initialize service."""
        self.repository = repository
        self.metrics = metrics
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    async def get_by_id(
        self,
        id: Union[str, UUID],
        *,
        use_cache: bool = True
    ) -> T:
        """Get entity by ID."""
        entity = await self.repository.get_by_id(id, use_cache=use_cache)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.repository.model.__name__} not found"
            )
        return entity

    async def find_one(
        self,
        *conditions: Any,
        **filters: Any
    ) -> Optional[T]:
        """Find single entity by conditions."""
        return await self.repository.find_one(*conditions, **filters)

    async def find_many(
        self,
        *conditions: Any,
        offset: int = 0,
        limit: int = 100,
        **filters: Any
    ) -> List[T]:
        """Find multiple entities by conditions."""
        return await self.repository.find_many(
            *conditions,
            offset=offset,
            limit=limit,
            **filters
        )

    async def create(
        self,
        data: Dict[str, Any]
    ) -> T:
        """Create new entity."""
        try:
            entity = await self.repository.create(data)
            if self.metrics:
                self.metrics.increment(f"{self.repository.model.__name__.lower()}.created")
            return entity
        except Exception as e:
            self.logger.error(f"Error creating entity: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.repository.model.__name__.lower()}.error.create")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating entity"
            )

    async def update(
        self,
        id: Union[str, UUID],
        data: Dict[str, Any]
    ) -> T:
        """Update existing entity."""
        entity = await self.get_by_id(id)
        try:
            updated = await self.repository.update(id, data)
            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.repository.model.__name__} not found"
                )
            if self.metrics:
                self.metrics.increment(f"{self.repository.model.__name__.lower()}.updated")
            return updated
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating entity: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.repository.model.__name__.lower()}.error.update")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating entity"
            )

    async def delete(
        self,
        id: Union[str, UUID]
    ) -> bool:
        """Delete entity by ID."""
        entity = await self.get_by_id(id)
        try:
            deleted = await self.repository.delete(id)
            if deleted and self.metrics:
                self.metrics.increment(f"{self.repository.model.__name__.lower()}.deleted")
            return deleted
        except Exception as e:
            self.logger.error(f"Error deleting entity: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment(f"{self.repository.model.__name__.lower()}.error.delete")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting entity"
            )

    async def count(
        self,
        *conditions: Any,
        **filters: Any
    ) -> int:
        """Count entities matching conditions."""
        return await self.repository.count(*conditions, **filters)

    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate data before create/update operations.
        
        Override this method in derived classes to add specific validation logic.
        """
        pass
