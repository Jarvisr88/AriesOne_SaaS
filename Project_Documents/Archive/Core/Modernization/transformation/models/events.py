"""
Events Model Module

This module provides event-related models and data structures.
"""
from typing import Optional, Any, Dict, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from enum import Enum

T = TypeVar('T')

class GridSourceType(str, Enum):
    """Enumeration of grid source types"""
    TABLE = "table"
    QUERY = "query"
    CUSTOM = "custom"
    VIRTUAL = "virtual"

class GridSource(BaseModel):
    """Base grid source model"""
    type: GridSourceType
    name: str
    schema: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CreateSourceEventArgs(GenericModel, Generic[T]):
    """
    Event arguments for source creation events.
    Generic type T represents the source type.
    """
    source: Optional[T] = None
    cancelled: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class SourceCreatedEvent(BaseModel):
    """Event data for when a source is created"""
    source_id: str
    source_type: GridSourceType
    timestamp: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SourceEventContext(BaseModel):
    """Context information for source events"""
    user_id: str
    session_id: str
    form_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
