"""Base repository interface module."""
from typing import TypeVar, Generic, Optional, List, Any
from uuid import UUID
from sqlalchemy import Select
from sqlalchemy.sql.expression import BinaryExpression

T = TypeVar('T')

class IRepository(Generic[T]):
    """Base repository interface for database operations."""

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID.
        
        Args:
            id: Entity ID.
            
        Returns:
            Optional entity.
        """
        raise NotImplementedError

    async def get_all(self) -> List[T]:
        """Get all entities.
        
        Returns:
            List of entities.
        """
        raise NotImplementedError

    async def find(self, *filters: BinaryExpression) -> List[T]:
        """Find entities by filters.
        
        Args:
            filters: SQLAlchemy filter expressions.
            
        Returns:
            List of matching entities.
        """
        raise NotImplementedError

    async def find_one(self, *filters: BinaryExpression) -> Optional[T]:
        """Find single entity by filters.
        
        Args:
            filters: SQLAlchemy filter expressions.
            
        Returns:
            Optional matching entity.
        """
        raise NotImplementedError

    async def add(self, entity: T) -> T:
        """Add new entity.
        
        Args:
            entity: Entity to add.
            
        Returns:
            Added entity.
        """
        raise NotImplementedError

    async def add_many(self, entities: List[T]) -> List[T]:
        """Add multiple entities.
        
        Args:
            entities: List of entities to add.
            
        Returns:
            List of added entities.
        """
        raise NotImplementedError

    async def update(self, entity: T) -> T:
        """Update existing entity.
        
        Args:
            entity: Entity to update.
            
        Returns:
            Updated entity.
        """
        raise NotImplementedError

    async def delete(self, entity: T) -> None:
        """Delete entity.
        
        Args:
            entity: Entity to delete.
        """
        raise NotImplementedError

    async def delete_by_id(self, id: UUID) -> None:
        """Delete entity by ID.
        
        Args:
            id: Entity ID.
        """
        raise NotImplementedError

    async def count(self, *filters: BinaryExpression) -> int:
        """Count entities matching filters.
        
        Args:
            filters: SQLAlchemy filter expressions.
            
        Returns:
            Count of matching entities.
        """
        raise NotImplementedError

    async def exists(self, *filters: BinaryExpression) -> bool:
        """Check if entities exist matching filters.
        
        Args:
            filters: SQLAlchemy filter expressions.
            
        Returns:
            True if matching entities exist.
        """
        raise NotImplementedError

    def query(self) -> Select:
        """Get base query for entity.
        
        Returns:
            SQLAlchemy select statement.
        """
        raise NotImplementedError
