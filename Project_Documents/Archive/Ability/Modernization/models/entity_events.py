"""
Entity Events Models Module

This module provides models for entity-related events.
"""
from typing import Any, Dict, Generic, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from uuid import UUID

T = TypeVar('T')
EntityID = Union[int, str, UUID]

class EventType(str, Enum):
    """Types of entity events"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    SOURCE_CREATED = "source_created"
    SOURCE_UPDATED = "source_updated"
    SOURCE_DELETED = "source_deleted"

class EventStatus(str, Enum):
    """Status of events"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class EventMetadata(BaseModel):
    """Model for event metadata"""
    event_id: UUID
    event_type: EventType
    status: EventStatus = EventStatus.PENDING
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EntityEvent(BaseModel, Generic[T]):
    """Base model for entity events"""
    metadata: EventMetadata
    entity_type: str
    entity_id: Optional[EntityID] = None
    payload: Optional[T] = None

class EntityCreatedEvent(EntityEvent[T]):
    """Event for entity creation"""
    entity_id: EntityID
    payload: T

    class Config:
        schema_extra = {
            "example": {
                "metadata": {
                    "event_id": "123e4567-e89b-12d3-a456-426614174000",
                    "event_type": EventType.CREATED,
                    "status": EventStatus.COMPLETED,
                    "timestamp": "2025-01-07T14:33:15",
                    "source": "user_service",
                    "correlation_id": "abc-123",
                    "causation_id": "def-456",
                    "metadata": {"user_id": "789"}
                },
                "entity_type": "user",
                "entity_id": "123",
                "payload": {"id": "123", "name": "John Doe"}
            }
        }

class GridSourceType(str, Enum):
    """Types of grid sources"""
    DATABASE = "database"
    FILE = "file"
    API = "api"
    MEMORY = "memory"
    CUSTOM = "custom"

class GridSourceConfig(BaseModel):
    """Configuration for grid sources"""
    source_type: GridSourceType
    connection_string: Optional[str] = None
    query: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GridSource(BaseModel):
    """Model for grid sources"""
    id: UUID
    name: str
    config: GridSourceConfig
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CreateSourceEvent(EntityEvent[GridSource]):
    """Event for grid source creation"""
    payload: GridSource

    class Config:
        schema_extra = {
            "example": {
                "metadata": {
                    "event_id": "123e4567-e89b-12d3-a456-426614174000",
                    "event_type": EventType.SOURCE_CREATED,
                    "status": EventStatus.COMPLETED,
                    "timestamp": "2025-01-07T14:33:15",
                    "source": "grid_service",
                    "correlation_id": "abc-123",
                    "causation_id": "def-456",
                    "metadata": {"user_id": "789"}
                },
                "entity_type": "grid_source",
                "entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "payload": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Users Grid",
                    "config": {
                        "source_type": GridSourceType.DATABASE,
                        "connection_string": "postgresql://localhost:5432/db",
                        "query": "SELECT * FROM users",
                        "parameters": {"limit": 100},
                        "metadata": {"cache_ttl": 300}
                    },
                    "metadata": {"created_by": "789"}
                }
            }
        }
