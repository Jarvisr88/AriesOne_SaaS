"""
Core Event Handler Base Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides the base implementation for all event handlers in the system.
"""
from abc import ABC
from datetime import datetime
from typing import Any, Dict, Generic, Optional, TypeVar
from uuid import UUID

from ..interfaces import IEntity, IEventHandler

T = TypeVar('T', bound=IEntity)


class EventHandlerBase(IEventHandler[T], Generic[T], ABC):
    """Base class for all event handlers providing common functionality."""
    
    async def handle_created(self, entity: T) -> None:
        """Handle entity creation event."""
        await self._log_event('created', entity)
        await self._notify_subscribers('created', entity)
    
    async def handle_updated(self, entity: T, changes: Dict[str, Any]) -> None:
        """Handle entity update event."""
        await self._log_event('updated', entity, changes)
        await self._notify_subscribers('updated', entity, changes)
    
    async def handle_deleted(self, entity_id: UUID) -> None:
        """Handle entity deletion event."""
        await self._log_event('deleted', None, {'entity_id': entity_id})
        await self._notify_subscribers('deleted', None, {'entity_id': entity_id})
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle error event."""
        await self._log_error(error, context)
        await self._notify_error_handlers(error, context)
    
    async def handle_validation(self, entity: T, validation_result: Dict[str, Any]) -> None:
        """Handle validation event."""
        await self._log_event('validation', entity, validation_result)
        if not validation_result.get('is_valid', False):
            await self._handle_validation_failure(entity, validation_result)
    
    async def handle_state_change(self, entity: T, old_state: str, new_state: str) -> None:
        """Handle entity state change event."""
        changes = {'old_state': old_state, 'new_state': new_state}
        await self._log_event('state_change', entity, changes)
        await self._notify_subscribers('state_change', entity, changes)
    
    async def _log_event(self, event_type: str, entity: Optional[T] = None,
                        details: Optional[Dict[str, Any]] = None) -> None:
        """Log an event to the event store."""
        event_data = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'entity_type': entity.__class__.__name__ if entity else None,
            'entity_id': str(entity.id) if entity else None,
            'details': details or {}
        }
        # Implement actual logging logic in subclasses
        await self._persist_event(event_data)
    
    async def _log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Log an error event."""
        error_data = {
            'error_type': error.__class__.__name__,
            'error_message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'context': context
        }
        # Implement actual error logging logic in subclasses
        await self._persist_error(error_data)
    
    async def _notify_subscribers(self, event_type: str, entity: Optional[T] = None,
                                details: Optional[Dict[str, Any]] = None) -> None:
        """Notify event subscribers."""
        # Implement notification logic in subclasses
        pass
    
    async def _notify_error_handlers(self, error: Exception,
                                   context: Dict[str, Any]) -> None:
        """Notify error handlers."""
        # Implement error notification logic in subclasses
        pass
    
    async def _handle_validation_failure(self, entity: T,
                                       validation_result: Dict[str, Any]) -> None:
        """Handle validation failure."""
        # Implement validation failure handling in subclasses
        pass
    
    async def _persist_event(self, event_data: Dict[str, Any]) -> None:
        """Persist event data."""
        # Implement event persistence logic in subclasses
        pass
    
    async def _persist_error(self, error_data: Dict[str, Any]) -> None:
        """Persist error data."""
        # Implement error persistence logic in subclasses
        pass
