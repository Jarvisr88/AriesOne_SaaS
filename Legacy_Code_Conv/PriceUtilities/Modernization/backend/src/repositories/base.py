"""
Base Repository Module
Version: 1.0.0
Last Updated: 2025-01-12

This module provides the base repository interface and implementation.
"""
from typing import Generic, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from core.database import Base

T = TypeVar('T', bound=Base)

class IRepository(Generic[T]):
    """Base repository interface."""
    
    def get(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        raise NotImplementedError
    
    def get_all(self) -> List[T]:
        """Get all entities."""
        raise NotImplementedError
    
    def create(self, entity: T) -> T:
        """Create new entity."""
        raise NotImplementedError
    
    def update(self, entity: T) -> T:
        """Update existing entity."""
        raise NotImplementedError
    
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        raise NotImplementedError

class SQLAlchemyRepository(IRepository[T]):
    """Base SQLAlchemy repository implementation."""
    
    def __init__(self, session: Session, model_type: Type[T]):
        self._session = session
        self._model_type = model_type
    
    def get(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        return self._session.get(self._model_type, id)
    
    def get_all(self) -> List[T]:
        """Get all entities."""
        stmt = select(self._model_type)
        return list(self._session.execute(stmt).scalars().all())
    
    def create(self, entity: T) -> T:
        """Create new entity."""
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return entity
    
    def update(self, entity: T) -> T:
        """Update existing entity."""
        self._session.merge(entity)
        self._session.commit()
        self._session.refresh(entity)
        return entity
    
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        entity = self.get(id)
        if entity:
            self._session.delete(entity)
            self._session.commit()
            return True
        return False
    
    def bulk_create(self, entities: List[T]) -> List[T]:
        """Create multiple entities."""
        self._session.add_all(entities)
        self._session.commit()
        for entity in entities:
            self._session.refresh(entity)
        return entities
    
    def bulk_update(self, entities: List[T]) -> List[T]:
        """Update multiple entities."""
        for entity in entities:
            self._session.merge(entity)
        self._session.commit()
        return entities
