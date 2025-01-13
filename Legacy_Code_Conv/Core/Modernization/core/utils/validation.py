"""
Core Validation Utility Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides validation utilities for the core module.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Pattern, Union
from uuid import UUID

from pydantic import BaseModel, ValidationError


class ValidationResult(BaseModel):
    """Validation result model."""
    is_valid: bool
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []


class ValidationRule(BaseModel):
    """Base validation rule model."""
    field: str
    message: str
    severity: str = "error"  # error or warning

    def validate(self, value: Any) -> Optional[Dict[str, Any]]:
        """Validate a value against the rule."""
        raise NotImplementedError


class RequiredRule(ValidationRule):
    """Required field validation rule."""
    
    def validate(self, value: Any) -> Optional[Dict[str, Any]]:
        """Validate required field."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return {
                "field": self.field,
                "message": self.message or f"{self.field} is required",
                "severity": self.severity
            }
        return None


class RegexRule(ValidationRule):
    """Regex pattern validation rule."""
    pattern: str
    flags: int = 0
    _compiled_pattern: Optional[Pattern] = None
    
    def __init__(self, **data: Any):
        """Initialize regex rule."""
        super().__init__(**data)
        self._compiled_pattern = re.compile(self.pattern, self.flags)
    
    def validate(self, value: Any) -> Optional[Dict[str, Any]]:
        """Validate value against regex pattern."""
        if not value or not isinstance(value, str):
            return None
            
        if not self._compiled_pattern.match(value):
            return {
                "field": self.field,
                "message": self.message or f"{self.field} does not match pattern",
                "severity": self.severity
            }
        return None


class RangeRule(ValidationRule):
    """Range validation rule."""
    min_value: Optional[Union[int, float, datetime]] = None
    max_value: Optional[Union[int, float, datetime]] = None
    
    def validate(self, value: Any) -> Optional[Dict[str, Any]]:
        """Validate value is within range."""
        if value is None:
            return None
            
        if self.min_value is not None and value < self.min_value:
            return {
                "field": self.field,
                "message": self.message or f"{self.field} is below minimum value",
                "severity": self.severity
            }
            
        if self.max_value is not None and value > self.max_value:
            return {
                "field": self.field,
                "message": self.message or f"{self.field} is above maximum value",
                "severity": self.severity
            }
        return None


class LengthRule(ValidationRule):
    """String length validation rule."""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    
    def validate(self, value: Any) -> Optional[Dict[str, Any]]:
        """Validate string length."""
        if not value or not isinstance(value, str):
            return None
            
        if self.min_length is not None and len(value) < self.min_length:
            return {
                "field": self.field,
                "message": self.message or f"{self.field} is too short",
                "severity": self.severity
            }
            
        if self.max_length is not None and len(value) > self.max_length:
            return {
                "field": self.field,
                "message": self.message or f"{self.field} is too long",
                "severity": self.severity
            }
        return None


class Validator:
    """Generic validator for applying multiple rules."""
    
    def __init__(self, rules: List[ValidationRule]):
        """Initialize validator with rules."""
        self.rules = rules
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against all rules."""
        result = ValidationResult(is_valid=True)
        
        for rule in self.rules:
            field_value = data.get(rule.field)
            validation_error = rule.validate(field_value)
            
            if validation_error:
                if validation_error["severity"] == "error":
                    result.is_valid = False
                    result.errors.append(validation_error)
                else:
                    result.warnings.append(validation_error)
        
        return result


# Common validation patterns
PATTERNS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "phone": r"^\+?1?\d{9,15}$",
    "url": r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$",
    "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    "username": r"^[a-zA-Z0-9_-]{3,16}$",
    "password": r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
}
