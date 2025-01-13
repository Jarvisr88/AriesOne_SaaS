"""
Core Entity Interface Module
Version: 1.0.0
Last Updated: 2025-01-10

This module defines the base interface for all entities in the system.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID


class IEntity(ABC):
    """Base interface for all entities in the system."""
    
    @property
    @abstractmethod
    def id(self) -> UUID:
        """Get the unique identifier for the entity."""
        pass
    
    @property
    @abstractmethod
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        pass
    
    @property
    @abstractmethod
    def updated_at(self) -> datetime:
        """Get the last update timestamp."""
        pass
    
    @property
    @abstractmethod
    def created_by(self) -> UUID:
        """Get the ID of the user who created this entity."""
        pass
    
    @property
    @abstractmethod
    def updated_by(self) -> UUID:
        """Get the ID of the user who last updated this entity."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary representation."""
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Update the entity from a dictionary representation."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the entity state."""
        pass
    
    @abstractmethod
    def get_audit_log(self) -> Dict[str, Any]:
        """Get audit information for the entity."""
        pass
