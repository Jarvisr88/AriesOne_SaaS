"""
Form Management API Endpoints Module

This module provides FastAPI endpoints for form management.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from ..models.form_management import (
    FormData,
    FormEvent,
    FormState,
    ValidationResult
)
from ..services.form_management_service import FormManagementService
from ..services.auth_service import get_current_user, User

router = APIRouter()

@router.post("/forms", response_model=FormData)
async def create_form(
    form_type: str,
    title: str,
    entity_id: Optional[Union[int, str, UUID]] = None,
    initial_data: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> FormData:
    """
    Create a new form.
    
    Args:
        form_type: Type of form
        title: Form title
        entity_id: Optional entity ID
        initial_data: Optional initial data
        metadata: Optional metadata
        current_user: The current authenticated user
        
    Returns:
        Created form data
    """
    service = FormManagementService()
    return await service.create_form(
        form_type,
        title,
        entity_id,
        initial_data,
        metadata
    )

@router.get("/forms/{form_id}", response_model=FormData)
async def get_form(
    form_id: UUID,
    current_user: User = Depends(get_current_user)
) -> FormData:
    """
    Get form by ID.
    
    Args:
        form_id: Form ID
        current_user: The current authenticated user
        
    Returns:
        Form data
        
    Raises:
        HTTPException: If form not found
    """
    service = FormManagementService()
    form = await service.get_form(form_id)
    if not form:
        raise HTTPException(
            status_code=404,
            detail=f"Form not found: {form_id}"
        )
    return form

@router.put("/forms/{form_id}", response_model=FormData)
async def update_form(
    form_id: UUID,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> FormData:
    """
    Update form data.
    
    Args:
        form_id: Form ID
        data: Updated data
        metadata: Optional metadata update
        current_user: The current authenticated user
        
    Returns:
        Updated form data
    """
    service = FormManagementService()
    return await service.update_form(form_id, data, metadata)

@router.post("/forms/{form_id}/validate", response_model=ValidationResult)
async def validate_form(
    form_id: UUID,
    current_user: User = Depends(get_current_user)
) -> ValidationResult:
    """
    Validate form data.
    
    Args:
        form_id: Form ID
        current_user: The current authenticated user
        
    Returns:
        Validation result
    """
    service = FormManagementService()
    return await service.validate_form(form_id)

@router.post("/forms/{form_id}/save", response_model=FormData)
async def save_form(
    form_id: UUID,
    current_user: User = Depends(get_current_user)
) -> FormData:
    """
    Save form data.
    
    Args:
        form_id: Form ID
        current_user: The current authenticated user
        
    Returns:
        Saved form data
    """
    service = FormManagementService()
    return await service.save_form(form_id)

@router.delete("/forms/{form_id}")
async def delete_form(
    form_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Delete form.
    
    Args:
        form_id: Form ID
        current_user: The current authenticated user
    """
    service = FormManagementService()
    await service.delete_form(form_id)
