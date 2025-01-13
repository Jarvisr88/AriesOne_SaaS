"""
Validation Framework Service Module

This module provides a comprehensive validation framework.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union, Callable, Type
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ValidationError
import re

class ValidationType(str, Enum):
    """Validation type enumeration"""
    REQUIRED = "required"
    TYPE = "type"
    FORMAT = "format"
    RANGE = "range"
    LENGTH = "length"
    PATTERN = "pattern"
    CUSTOM = "custom"
    DEPENDENCY = "dependency"
    UNIQUE = "unique"

class ValidationSeverity(str, Enum):
    """Validation severity enumeration"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationRule(BaseModel):
    """Validation rule definition"""
    rule_id: UUID = Field(default_factory=uuid4)
    field: str
    type: ValidationType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ValidationResult(BaseModel):
    """Validation result"""
    field: str
    rule_id: UUID
    valid: bool
    message: str
    severity: ValidationSeverity
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationContext(BaseModel):
    """Validation context"""
    entity_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ValidationFramework:
    """Validation framework service"""
    
    def __init__(self):
        """Initialize validation framework"""
        self._rules: Dict[str, List[ValidationRule]] = {}
        self._custom_validators: Dict[str, Callable] = {}
        self._type_validators: Dict[str, Type] = {}

    async def register_rule(
        self,
        entity_type: str,
        field: str,
        validation_type: ValidationType,
        parameters: Dict[str, Any],
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationRule:
        """Register a validation rule"""
        rule = ValidationRule(
            field=field,
            type=validation_type,
            parameters=parameters,
            message=message,
            severity=severity,
            enabled=enabled,
            metadata=metadata or {}
        )
        
        if entity_type not in self._rules:
            self._rules[entity_type] = []
        
        self._rules[entity_type].append(rule)
        return rule

    async def register_custom_validator(
        self,
        name: str,
        validator: Callable
    ):
        """Register a custom validator"""
        self._custom_validators[name] = validator

    async def register_type_validator(
        self,
        type_name: str,
        validator: Type
    ):
        """Register a type validator"""
        self._type_validators[type_name] = validator

    async def validate(
        self,
        context: ValidationContext
    ) -> List[ValidationResult]:
        """Validate data against rules"""
        results = []
        
        # Get rules for entity type
        rules = self._rules.get(context.entity_type, [])
        
        # Apply enabled rules
        for rule in [r for r in rules if r.enabled]:
            try:
                # Get field value
                field_value = context.data.get(rule.field)
                
                # Validate based on type
                if rule.type == ValidationType.REQUIRED:
                    valid = field_value is not None and field_value != ""
                
                elif rule.type == ValidationType.TYPE:
                    type_name = rule.parameters.get("type")
                    validator = self._type_validators.get(type_name)
                    if not validator:
                        raise ValueError(f"Type validator not found: {type_name}")
                    try:
                        validator(field_value)
                        valid = True
                    except (ValueError, ValidationError):
                        valid = False
                
                elif rule.type == ValidationType.FORMAT:
                    format_pattern = rule.parameters.get("pattern")
                    valid = bool(re.match(format_pattern, str(field_value)))
                
                elif rule.type == ValidationType.RANGE:
                    min_value = rule.parameters.get("min")
                    max_value = rule.parameters.get("max")
                    valid = True
                    if min_value is not None and field_value < min_value:
                        valid = False
                    if max_value is not None and field_value > max_value:
                        valid = False
                
                elif rule.type == ValidationType.LENGTH:
                    min_length = rule.parameters.get("min")
                    max_length = rule.parameters.get("max")
                    valid = True
                    if min_length is not None and len(field_value) < min_length:
                        valid = False
                    if max_length is not None and len(field_value) > max_length:
                        valid = False
                
                elif rule.type == ValidationType.PATTERN:
                    pattern = rule.parameters.get("pattern")
                    valid = bool(re.match(pattern, str(field_value)))
                
                elif rule.type == ValidationType.CUSTOM:
                    validator_name = rule.parameters.get("validator")
                    validator = self._custom_validators.get(validator_name)
                    if not validator:
                        raise ValueError(f"Custom validator not found: {validator_name}")
                    valid = await validator(field_value, context)
                
                elif rule.type == ValidationType.DEPENDENCY:
                    dependent_field = rule.parameters.get("field")
                    dependent_value = context.data.get(dependent_field)
                    condition = rule.parameters.get("condition")
                    valid = eval(condition, {"value": field_value, "dependent": dependent_value})
                
                elif rule.type == ValidationType.UNIQUE:
                    # Unique validation would typically involve database check
                    # This is a placeholder for actual implementation
                    valid = True
                
                else:
                    raise ValueError(f"Unknown validation type: {rule.type}")
                
                # Record result
                if not valid:
                    results.append(
                        ValidationResult(
                            field=rule.field,
                            rule_id=rule.rule_id,
                            valid=False,
                            message=rule.message,
                            severity=rule.severity,
                            metadata=rule.metadata
                        )
                    )
                
            except Exception as e:
                results.append(
                    ValidationResult(
                        field=rule.field,
                        rule_id=rule.rule_id,
                        valid=False,
                        message=f"Validation error: {str(e)}",
                        severity=ValidationSeverity.ERROR,
                        metadata={
                            "error": str(e),
                            "rule_type": rule.type
                        }
                    )
                )
        
        return results
