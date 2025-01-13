"""
Validation Models Module

This module provides models for entity validation and validation results.
"""
from typing import Optional, Dict, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from enum import Enum
from datetime import datetime

T = TypeVar('T')

class ValidationSeverity(str, Enum):
    """Enumeration of validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationCategory(str, Enum):
    """Enumeration of validation categories"""
    REQUIRED = "required"
    FORMAT = "format"
    RANGE = "range"
    CUSTOM = "custom"
    BUSINESS = "business"
    RELATIONSHIP = "relationship"

class ValidationScope(str, Enum):
    """Enumeration of validation scopes"""
    FIELD = "field"
    ENTITY = "entity"
    COLLECTION = "collection"
    CROSS_ENTITY = "cross_entity"

class ValidationResult(BaseModel):
    """Model for validation result"""
    field: Optional[str] = None
    message: str
    severity: ValidationSeverity
    category: ValidationCategory
    scope: ValidationScope
    code: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationContext(BaseModel):
    """Model for validation context"""
    entity_type: str
    operation: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EntityValidation(GenericModel, Generic[T]):
    """
    Model for entity validation.
    Generic type T represents the entity type.
    """
    entity: T
    is_valid: bool = True
    results: List[ValidationResult] = Field(default_factory=list)
    context: ValidationContext
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ValidationRule(BaseModel):
    """Model for validation rule definition"""
    name: str
    description: str
    category: ValidationCategory
    scope: ValidationScope
    severity: ValidationSeverity
    message_template: str
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ValidationRuleSet(BaseModel):
    """Model for validation rule set"""
    name: str
    description: str
    entity_type: str
    rules: List[ValidationRule] = Field(default_factory=list)
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

class ValidationSummary(BaseModel):
    """Model for validation summary"""
    total_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    categories: Dict[ValidationCategory, int] = Field(default_factory=dict)
    scopes: Dict[ValidationScope, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def update_counts(self, result: ValidationResult):
        """Update summary counts based on validation result"""
        self.total_count += 1
        if result.severity == ValidationSeverity.ERROR:
            self.error_count += 1
        elif result.severity == ValidationSeverity.WARNING:
            self.warning_count += 1
        elif result.severity == ValidationSeverity.INFO:
            self.info_count += 1
            
        self.categories[result.category] = self.categories.get(result.category, 0) + 1
        self.scopes[result.scope] = self.scopes.get(result.scope, 0) + 1
