"""
Form Entity Model Module

This module provides models for form entity maintenance and management.
"""
from typing import Optional, Dict, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

T = TypeVar('T')

class EntityState(str, Enum):
    """Enumeration of entity states"""
    NEW = "new"
    MODIFIED = "modified"
    DELETED = "deleted"
    UNCHANGED = "unchanged"

class ValidationSeverity(str, Enum):
    """Enumeration of validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationResult(BaseModel):
    """Model for validation results"""
    field: str
    message: str
    severity: ValidationSeverity
    code: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class EntityValidation(BaseModel):
    """Model for entity validation"""
    is_valid: bool
    results: List[ValidationResult] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EntityAudit(BaseModel):
    """Model for entity audit information"""
    created_at: datetime
    created_by: str
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None
    version: int = 1
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FormEntity(BaseModel, Generic[T]):
    """
    Model for form entities.
    Generic type T represents the entity data type.
    """
    id: str
    state: EntityState = EntityState.UNCHANGED
    data: T
    validation: EntityValidation = Field(default_factory=lambda: EntityValidation(is_valid=True))
    audit: EntityAudit
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class FormEntityCollection(BaseModel, Generic[T]):
    """
    Model for collections of form entities.
    Generic type T represents the entity data type.
    """
    entities: Dict[str, FormEntity[T]] = Field(default_factory=dict)
    validation: EntityValidation = Field(default_factory=lambda: EntityValidation(is_valid=True))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_entity(self, entity: FormEntity[T]):
        """Add an entity to the collection"""
        self.entities[entity.id] = entity
        self._validate_collection()
    
    def remove_entity(self, entity_id: str):
        """Remove an entity from the collection"""
        if entity_id in self.entities:
            del self.entities[entity_id]
            self._validate_collection()
    
    def get_entity(self, entity_id: str) -> Optional[FormEntity[T]]:
        """Get an entity by ID"""
        return self.entities.get(entity_id)
    
    def get_modified_entities(self) -> List[FormEntity[T]]:
        """Get all modified entities"""
        return [
            entity for entity in self.entities.values()
            if entity.state != EntityState.UNCHANGED
        ]
    
    def _validate_collection(self):
        """Validate the entire collection"""
        is_valid = True
        results = []
        
        for entity in self.entities.values():
            if not entity.validation.is_valid:
                is_valid = False
                results.extend(entity.validation.results)
        
        self.validation = EntityValidation(
            is_valid=is_valid,
            results=results
        )
