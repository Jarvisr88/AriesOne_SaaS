"""Event definitions and base classes."""
from typing import Any, Dict, Optional
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field

class EventType(str, Enum):
    """Event types."""
    
    # Entity events
    ENTITY_CREATED = "entity.created"
    ENTITY_UPDATED = "entity.updated"
    ENTITY_DELETED = "entity.deleted"
    
    # Business events
    SESSION_SCHEDULED = "session.scheduled"
    SESSION_STARTED = "session.started"
    SESSION_COMPLETED = "session.completed"
    
    # Integration events
    INTEGRATION_REQUESTED = "integration.requested"
    INTEGRATION_COMPLETED = "integration.completed"
    INTEGRATION_FAILED = "integration.failed"

class Event(BaseModel):
    """Base event model."""
    
    id: UUID = Field(default_factory=uuid4)
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"
    source: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class EntityEvent(Event):
    """Entity event model."""
    
    entity_type: str
    entity_id: UUID
    user_id: Optional[UUID] = None

class IntegrationEvent(Event):
    """Integration event model."""
    
    integration_type: str
    status: str
    error_message: Optional[str] = None

class EventPublisher(BaseModel):
    """Event metadata for publishing."""
    
    topic: str
    partition_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    
    @classmethod
    def for_entity(
        cls,
        entity_type: str,
        event_type: EventType
    ) -> "EventPublisher":
        """Create publisher for entity event.
        
        Args:
            entity_type: Type of entity.
            event_type: Type of event.
            
        Returns:
            Event publisher.
        """
        return cls(
            topic=f"{entity_type}.events",
            partition_key=event_type.value,
            headers={"event_type": event_type.value}
        )
    
    @classmethod
    def for_integration(
        cls,
        integration_type: str,
        event_type: EventType
    ) -> "EventPublisher":
        """Create publisher for integration event.
        
        Args:
            integration_type: Type of integration.
            event_type: Type of event.
            
        Returns:
            Event publisher.
        """
        return cls(
            topic=f"{integration_type}.events",
            partition_key=event_type.value,
            headers={"event_type": event_type.value}
        )
