"""Base repository implementation module."""
from typing import TypeVar, Generic, Optional, List, Type
from uuid import UUID
from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import BinaryExpression

from core.interfaces.repository import IRepository
from infrastructure.database.base import Base

T = TypeVar('T', bound=Base)

class Repository(IRepository[T], Generic[T]):
    """Base repository implementation."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        """Initialize repository.
        
        Args:
            session: Database session.
            model: SQLAlchemy model class.
        """
        self._session = session
        self._model = model

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID."""
        return await self._session.get(self._model, id)

    async def get_all(self) -> List[T]:
        """Get all entities."""
        result = await self._session.execute(select(self._model))
        return list(result.scalars().all())

    async def find(self, *filters: BinaryExpression) -> List[T]:
        """Find entities by filters."""
        query = select(self._model)
        if filters:
            query = query.where(*filters)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def find_one(self, *filters: BinaryExpression) -> Optional[T]:
        """Find single entity by filters."""
        query = select(self._model)
        if filters:
            query = query.where(*filters)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def add(self, entity: T) -> T:
        """Add new entity."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def add_many(self, entities: List[T]) -> List[T]:
        """Add multiple entities."""
        self._session.add_all(entities)
        await self._session.flush()
        for entity in entities:
            await self._session.refresh(entity)
        return entities

    async def update(self, entity: T) -> T:
        """Update existing entity."""
        await self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        """Delete entity."""
        await self._session.delete(entity)
        await self._session.flush()

    async def delete_by_id(self, id: UUID) -> None:
        """Delete entity by ID."""
        entity = await self.get_by_id(id)
        if entity:
            await self.delete(entity)

    async def count(self, *filters: BinaryExpression) -> int:
        """Count entities matching filters."""
        query = select(func.count()).select_from(self._model)
        if filters:
            query = query.where(*filters)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def exists(self, *filters: BinaryExpression) -> bool:
        """Check if entities exist matching filters."""
        count = await self.count(*filters)
        return count > 0

    def query(self) -> Select:
        """Get base query for entity."""
        return select(self._model)
