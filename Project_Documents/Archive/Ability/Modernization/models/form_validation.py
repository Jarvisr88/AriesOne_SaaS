"""
Form Validation Models Module

This module provides models for form entity validation.
"""
from typing import Optional, Dict, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from enum import Enum
from datetime import datetime

T = TypeVar('T')

class ErrorSeverity(str, Enum):
    """Enumeration of error severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationError(BaseModel):
    """Model for validation error"""
    field: Optional[str] = None
    message: str
    is_error: bool = True  # True for errors, False for warnings
    code: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationResult(BaseModel):
    """Model for validation results"""
    values: Dict[str, List[ValidationError]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def add_error(self, field: Optional[str], message: str, is_error: bool = True):
        """Add an error to the validation results"""
        if field not in self.values:
            self.values[field or ""] = []
        
        self.values[field or ""].append(
            ValidationError(
                field=field,
                message=message,
                is_error=is_error
            )
        )
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return any(
            error.is_error
            for errors in self.values.values()
            for error in errors
        )
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return any(
            not error.is_error
            for errors in self.values.values()
            for error in errors
        )
    
    def get_error_messages(self) -> List[str]:
        """Get all error messages"""
        return [
            error.message
            for errors in self.values.values()
            for error in errors
            if error.is_error
        ]
    
    def get_warning_messages(self) -> List[str]:
        """Get all warning messages"""
        return [
            error.message
            for errors in self.values.values()
            for error in errors
            if not error.is_error
        ]

class EntityValidator(GenericModel, Generic[T]):
    """
    Model for entity validator.
    Generic type T represents the entity type.
    """
    entity: T
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def validate(self) -> ValidationResult:
        """
        Validate the entity.
        Override this method to implement validation logic.
        
        Returns:
            Validation results
        """
        return ValidationResult()
