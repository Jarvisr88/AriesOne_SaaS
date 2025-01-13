"""
Core Entity Base Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides the base implementation for all entities in the system.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

from ..interfaces import IEntity


class EntityBase(BaseModel, IEntity):
    """Base class for all entities providing common functionality."""
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    version: int = Field(default=1, ge=1)
    is_active: bool = True
    
    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return self.dict(exclude_none=True)
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Update entity from dictionary."""
        for field, value in data.items():
            if hasattr(self, field):
                setattr(self, field, value)
        self.updated_at = datetime.utcnow()
        self.version += 1
    
    def validate(self) -> bool:
        """Validate entity state."""
        try:
            self.validate_fields()
            return True
        except ValueError:
            return False
    
    def validate_fields(self) -> None:
        """Validate individual fields. Override in subclasses."""
        pass
    
    def get_audit_log(self) -> Dict[str, Any]:
        """Get audit information."""
        return {
            'entity_id': str(self.id),
            'entity_type': self.__class__.__name__,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_at': self.updated_at.isoformat(),
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'is_active': self.is_active
        }
    
    @validator('updated_at')
    def validate_updated_at(cls, v: datetime, values: Dict[str, Any]) -> datetime:
        """Ensure updated_at is not before created_at."""
        if 'created_at' in values and v < values['created_at']:
            raise ValueError('updated_at cannot be before created_at')
        return v
    
    def __str__(self) -> str:
        """String representation of the entity."""
        return f"{self.__class__.__name__}(id={self.id})"
