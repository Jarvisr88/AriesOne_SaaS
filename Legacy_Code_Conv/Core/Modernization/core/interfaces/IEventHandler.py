"""
Core Event Handler Interface Module
Version: 1.0.0
Last Updated: 2025-01-10

This module defines the base interface for all event handlers in the system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar
from uuid import UUID

from .IEntity import IEntity

T = TypeVar('T', bound=IEntity)


class IEventHandler(Generic[T], ABC):
    """Base interface for all event handlers in the system."""
    
    @abstractmethod
    async def handle_created(self, entity: T) -> None:
        """Handle entity creation event."""
        pass
    
    @abstractmethod
    async def handle_updated(self, entity: T, changes: Dict[str, Any]) -> None:
        """Handle entity update event."""
        pass
    
    @abstractmethod
    async def handle_deleted(self, entity_id: UUID) -> None:
        """Handle entity deletion event."""
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle error event."""
        pass
    
    @abstractmethod
    async def handle_validation(self, entity: T, validation_result: Dict[str, Any]) -> None:
        """Handle validation event."""
        pass
    
    @abstractmethod
    async def handle_state_change(self, entity: T, old_state: str, new_state: str) -> None:
        """Handle entity state change event."""
        pass
