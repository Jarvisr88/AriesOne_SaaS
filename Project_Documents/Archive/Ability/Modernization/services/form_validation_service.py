"""
Form Validation Service Module

This module provides services for form entity validation.
"""
from typing import Optional, Dict, Any, List, Generic, TypeVar, Callable
from ..models.form_validation import (
    ValidationResult,
    ValidationError,
    EntityValidator
)
from .base_service import BaseService
from fastapi import HTTPException
import uuid
from datetime import datetime

T = TypeVar('T')

class FormValidationService(BaseService, Generic[T]):
    """Service for handling form entity validation"""
    
    def __init__(self):
        """Initialize form validation service"""
        self._validators: Dict[str, List[Callable[[T], ValidationResult]]] = {}
    
    async def validate_entity(
        self,
        entity_type: str,
        entity: T
    ) -> ValidationResult:
        """
        Validate an entity.
        
        Args:
            entity_type: Type of entity
            entity: Entity to validate
            
        Returns:
            Validation results
        """
        result = ValidationResult()
        
        # Run validators for entity type
        if entity_type in self._validators:
            for validator in self._validators[entity_type]:
                try:
                    validator_result = await validator(entity)
                    # Merge validator results
                    for field, errors in validator_result.values.items():
                        if field not in result.values:
                            result.values[field] = []
                        result.values[field].extend(errors)
                except Exception as e:
                    result.add_error(
                        field=None,
                        message=f"Validator error: {str(e)}",
                        is_error=True
                    )
        
        return result
    
    async def add_validator(
        self,
        entity_type: str,
        validator: Callable[[T], ValidationResult]
    ):
        """
        Add a validator for an entity type.
        
        Args:
            entity_type: Type of entity to validate
            validator: Validation function
        """
        if entity_type not in self._validators:
            self._validators[entity_type] = []
        self._validators[entity_type].append(validator)
    
    async def remove_validator(
        self,
        entity_type: str,
        validator: Callable[[T], ValidationResult]
    ):
        """
        Remove a validator for an entity type.
        
        Args:
            entity_type: Type of entity
            validator: Validator to remove
        """
        if entity_type in self._validators:
            validators = self._validators[entity_type]
            if validator in validators:
                validators.remove(validator)
    
    async def format_validation_message(
        self,
        result: ValidationResult,
        title: str
    ) -> Optional[str]:
        """
        Format validation result as a user-friendly message.
        
        Args:
            result: Validation result
            title: Message title
            
        Returns:
            Formatted message if there are errors/warnings, None otherwise
        """
        if result.has_errors():
            # Format error message
            message = ["There are some errors in the input data:"]
            for error_msg in result.get_error_messages():
                message.append(f"- {error_msg}")
            message.extend(["", "Cannot proceed."])
            return "\n".join(message)
        
        if result.has_warnings():
            # Format warning message
            message = ["There are some warnings in the input data:"]
            for warning_msg in result.get_warning_messages():
                message.append(f"- {warning_msg}")
            message.extend(["", "Do you want to proceed?"])
            return "\n".join(message)
        
        return None
