"""
Validation API Endpoints Module

This module provides FastAPI endpoints for entity validation.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from ..models.validation import (
    ValidationResult,
    ValidationContext,
    EntityValidation,
    ValidationRule,
    ValidationRuleSet,
    ValidationSummary
)
from ..services.validation_service import ValidationService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.post("/validation/rule-sets", response_model=str)
async def create_rule_set(
    rule_set: ValidationRuleSet,
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Create a new validation rule set.
    
    Args:
        rule_set: Validation rule set to create
        current_user: The current authenticated user
        
    Returns:
        Rule set ID
    """
    service = ValidationService[Dict[str, Any]]()
    return await service.create_rule_set(rule_set)

@router.post("/validation/entities", response_model=EntityValidation[Dict[str, Any]])
async def validate_entity(
    entity: Dict[str, Any],
    context: ValidationContext,
    current_user: User = Depends(get_current_user)
) -> EntityValidation[Dict[str, Any]]:
    """
    Validate an entity.
    
    Args:
        entity: Entity to validate
        context: Validation context
        current_user: The current authenticated user
        
    Returns:
        Validation results
    """
    service = ValidationService[Dict[str, Any]]()
    return await service.validate_entity(entity, context)

@router.get("/validation/rule-sets/{rule_set_id}", response_model=ValidationRuleSet)
async def get_rule_set(
    rule_set_id: str,
    current_user: User = Depends(get_current_user)
) -> ValidationRuleSet:
    """
    Get a validation rule set.
    
    Args:
        rule_set_id: ID of the rule set
        current_user: The current authenticated user
        
    Returns:
        Validation rule set
    """
    service = ValidationService[Dict[str, Any]]()
    return await service.get_rule_set(rule_set_id)

@router.put("/validation/rule-sets/{rule_set_id}")
async def update_rule_set(
    rule_set_id: str,
    rule_set: ValidationRuleSet,
    current_user: User = Depends(get_current_user)
):
    """
    Update a validation rule set.
    
    Args:
        rule_set_id: ID of the rule set
        rule_set: Updated rule set
        current_user: The current authenticated user
    """
    service = ValidationService[Dict[str, Any]]()
    await service.update_rule_set(rule_set_id, rule_set)

@router.delete("/validation/rule-sets/{rule_set_id}")
async def delete_rule_set(
    rule_set_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a validation rule set.
    
    Args:
        rule_set_id: ID of the rule set to delete
        current_user: The current authenticated user
    """
    service = ValidationService[Dict[str, Any]]()
    await service.delete_rule_set(rule_set_id)

@router.get("/validation/rule-sets/entity/{entity_type}", response_model=List[ValidationRuleSet])
async def get_rule_sets_for_entity(
    entity_type: str,
    current_user: User = Depends(get_current_user)
) -> List[ValidationRuleSet]:
    """
    Get all validation rule sets for an entity type.
    
    Args:
        entity_type: Type of entity
        current_user: The current authenticated user
        
    Returns:
        List of validation rule sets
    """
    service = ValidationService[Dict[str, Any]]()
    return await service.get_rule_sets_for_entity(entity_type)
