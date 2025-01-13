"""
Core Repository Interface Module
Version: 1.0.0
Last Updated: 2025-01-10

This module defines the base interface for all repositories in the system.
"""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar, Any, Dict
from uuid import UUID

from .IEntity import IEntity

T = TypeVar('T', bound=IEntity)


class IRepository(Generic[T], ABC):
    """Base interface for all repositories in the system."""
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Retrieve an entity by its ID."""
        pass
    
    @abstractmethod
    async def get_all(self, filter_params: Optional[Dict[str, Any]] = None) -> List[T]:
        """Retrieve all entities matching the filter parameters."""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete an entity by its ID."""
        pass
    
    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        """Check if an entity exists."""
        pass
    
    @abstractmethod
    async def count(self, filter_params: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching the filter parameters."""
        pass
    
    @abstractmethod
    async def get_page(self, page: int, page_size: int, 
                      filter_params: Optional[Dict[str, Any]] = None,
                      sort_params: Optional[Dict[str, str]] = None) -> List[T]:
        """Get a paginated list of entities."""
        pass
