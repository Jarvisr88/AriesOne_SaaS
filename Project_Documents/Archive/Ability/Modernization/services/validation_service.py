"""
Validation Service Module

This module provides services for entity validation.
"""
from typing import Optional, Dict, Any, List, Generic, TypeVar, Callable
from ..models.validation import (
    ValidationResult,
    ValidationSeverity,
    ValidationCategory,
    ValidationScope,
    ValidationContext,
    EntityValidation,
    ValidationRule,
    ValidationRuleSet,
    ValidationSummary
)
from .base_service import BaseService
from fastapi import HTTPException
import uuid
from datetime import datetime

T = TypeVar('T')

class ValidationService(BaseService, Generic[T]):
    """Service for handling entity validation"""
    
    def __init__(self):
        """Initialize validation service"""
        self._rule_sets: Dict[str, ValidationRuleSet] = {}
        self._validators: Dict[str, List[Callable[[T, ValidationContext], List[ValidationResult]]]] = {}
    
    async def create_rule_set(
        self,
        rule_set: ValidationRuleSet
    ) -> str:
        """
        Create a new validation rule set.
        
        Args:
            rule_set: Validation rule set to create
            
        Returns:
            Rule set ID
        """
        rule_set_id = str(uuid.uuid4())
        self._rule_sets[rule_set_id] = rule_set
        return rule_set_id
    
    async def validate_entity(
        self,
        entity: T,
        context: ValidationContext
    ) -> EntityValidation[T]:
        """
        Validate an entity.
        
        Args:
            entity: Entity to validate
            context: Validation context
            
        Returns:
            Validation results
        """
        results: List[ValidationResult] = []
        
        # Run validators for entity type
        if context.entity_type in self._validators:
            for validator in self._validators[context.entity_type]:
                try:
                    validator_results = await validator(entity, context)
                    results.extend(validator_results)
                except Exception as e:
                    results.append(
                        ValidationResult(
                            message=f"Validator error: {str(e)}",
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.CUSTOM,
                            scope=ValidationScope.ENTITY
                        )
                    )
        
        # Create validation summary
        summary = ValidationSummary()
        for result in results:
            summary.update_counts(result)
        
        # Create entity validation
        validation = EntityValidation(
            entity=entity,
            is_valid=summary.error_count == 0,
            results=results,
            context=context,
            metadata={
                "summary": summary.dict()
            }
        )
        
        return validation
    
    async def add_validator(
        self,
        entity_type: str,
        validator: Callable[[T, ValidationContext], List[ValidationResult]]
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
        validator: Callable[[T, ValidationContext], List[ValidationResult]]
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
    
    async def get_rule_set(
        self,
        rule_set_id: str
    ) -> ValidationRuleSet:
        """
        Get a validation rule set.
        
        Args:
            rule_set_id: ID of the rule set
            
        Returns:
            Validation rule set
            
        Raises:
            HTTPException: If rule set is not found
        """
        rule_set = self._rule_sets.get(rule_set_id)
        if not rule_set:
            raise HTTPException(
                status_code=404,
                detail=f"Rule set not found: {rule_set_id}"
            )
        return rule_set
    
    async def update_rule_set(
        self,
        rule_set_id: str,
        rule_set: ValidationRuleSet
    ):
        """
        Update a validation rule set.
        
        Args:
            rule_set_id: ID of the rule set
            rule_set: Updated rule set
            
        Raises:
            HTTPException: If rule set is not found
        """
        if rule_set_id not in self._rule_sets:
            raise HTTPException(
                status_code=404,
                detail=f"Rule set not found: {rule_set_id}"
            )
        rule_set.modified_at = datetime.utcnow()
        self._rule_sets[rule_set_id] = rule_set
    
    async def delete_rule_set(
        self,
        rule_set_id: str
    ):
        """
        Delete a validation rule set.
        
        Args:
            rule_set_id: ID of the rule set to delete
            
        Raises:
            HTTPException: If rule set is not found
        """
        if rule_set_id not in self._rule_sets:
            raise HTTPException(
                status_code=404,
                detail=f"Rule set not found: {rule_set_id}"
            )
        del self._rule_sets[rule_set_id]
    
    async def get_rule_sets_for_entity(
        self,
        entity_type: str
    ) -> List[ValidationRuleSet]:
        """
        Get all validation rule sets for an entity type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            List of validation rule sets
        """
        return [
            rule_set for rule_set in self._rule_sets.values()
            if rule_set.entity_type == entity_type and rule_set.enabled
        ]
