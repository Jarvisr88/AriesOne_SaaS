"""
Form endpoints for the Core module.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...services.form_service import FormService
from ...models.form import (
    FormDefinition, FormState, FormValidation,
    FormDefinitionSchema, FormStateSchema
)
from ...database import get_session
from ...dependencies import get_current_active_user, check_permission
from ...auth.models import UserInDB

router = APIRouter(prefix="/forms", tags=["forms"])

@router.post("/", response_model=FormDefinition)
async def create_form(
    form_schema: FormDefinitionSchema,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("forms:create"))
) -> FormDefinition:
    """Create a new form definition."""
    form_service = FormService(session)
    return await form_service.create_form_definition(form_schema)

@router.get("/{form_id}", response_model=FormDefinition)
async def get_form(
    form_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("forms:read"))
) -> FormDefinition:
    """Get form definition by ID."""
    form_service = FormService(session)
    form = await form_service.get_form_definition(form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form {form_id} not found"
        )
    return form

@router.put("/{form_id}", response_model=FormDefinition)
async def update_form(
    form_id: int,
    form_schema: FormDefinitionSchema,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("forms:update"))
) -> FormDefinition:
    """Update form definition."""
    form_service = FormService(session)
    return await form_service.update_form_definition(form_id, form_schema)

@router.get("/{form_id}/state/{entity_id}", response_model=FormState)
async def get_form_state(
    form_id: int,
    entity_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("forms:read"))
) -> FormState:
    """Get form state for an entity."""
    form_service = FormService(session)
    state = await form_service.get_form_state(form_id, entity_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form state not found for form {form_id} and entity {entity_id}"
        )
    return state

@router.post("/state", response_model=FormState)
async def save_form_state(
    state_schema: FormStateSchema,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("forms:update"))
) -> FormState:
    """Save form state."""
    form_service = FormService(session)
    return await form_service.save_form_state(state_schema)

@router.post("/{form_id}/validate/{entity_id}", response_model=List[FormValidation])
async def validate_form(
    form_id: int,
    entity_id: int,
    data: dict,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("forms:validate"))
) -> List[FormValidation]:
    """Validate form data."""
    form_service = FormService(session)
    return await form_service.validate_form(form_id, entity_id, data)

@router.post("/{form_id}/publish")
async def publish_form(
    form_id: int,
    current_user: UserInDB = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _=Depends(check_permission("forms:publish"))
) -> dict:
    """Publish a form definition."""
    form_service = FormService(session)
    await form_service.publish_form(form_id)
    return {"message": f"Form {form_id} published successfully"}
