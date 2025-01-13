"""
Core Repository Base Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides the base implementation for all repositories in the system.
"""
from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Select

from ..interfaces import IEntity, IRepository

T = TypeVar('T', bound=IEntity)


class RepositoryBase(IRepository[T], Generic[T], ABC):
    """Base class for all repositories providing common functionality."""
    
    def __init__(self, session: AsyncSession, model_type: Type[T]):
        """Initialize repository with session and model type."""
        self._session = session
        self._model_type = model_type
    
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Retrieve an entity by its ID."""
        stmt = select(self._model_type).where(self._model_type.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, filter_params: Optional[Dict[str, Any]] = None) -> List[T]:
        """Retrieve all entities matching the filter parameters."""
        stmt = select(self._model_type)
        if filter_params:
            stmt = self._apply_filters(stmt, filter_params)
        result = await self._session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
    
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        await self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
    
    async def delete(self, id: UUID) -> bool:
        """Delete an entity by its ID."""
        entity = await self.get_by_id(id)
        if entity:
            await self._session.delete(entity)
            await self._session.flush()
            return True
        return False
    
    async def exists(self, id: UUID) -> bool:
        """Check if an entity exists."""
        stmt = select(self._model_type.id).where(self._model_type.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def count(self, filter_params: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching the filter parameters."""
        stmt = select(self._model_type)
        if filter_params:
            stmt = self._apply_filters(stmt, filter_params)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())
    
    async def get_page(self, page: int, page_size: int,
                      filter_params: Optional[Dict[str, Any]] = None,
                      sort_params: Optional[Dict[str, str]] = None) -> List[T]:
        """Get a paginated list of entities."""
        stmt = select(self._model_type)
        if filter_params:
            stmt = self._apply_filters(stmt, filter_params)
        if sort_params:
            stmt = self._apply_sorting(stmt, sort_params)
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(stmt)
        return result.scalars().all()
    
    def _apply_filters(self, stmt: Select, filter_params: Dict[str, Any]) -> Select:
        """Apply filters to the query. Override in subclasses for custom filtering."""
        for field, value in filter_params.items():
            if hasattr(self._model_type, field):
                stmt = stmt.where(getattr(self._model_type, field) == value)
        return stmt
    
    def _apply_sorting(self, stmt: Select, sort_params: Dict[str, str]) -> Select:
        """Apply sorting to the query. Override in subclasses for custom sorting."""
        for field, direction in sort_params.items():
            if hasattr(self._model_type, field):
                column = getattr(self._model_type, field)
                stmt = stmt.order_by(column.desc() if direction.lower() == 'desc' else column.asc())
        return stmt
