"""Form endpoints.

This module provides API endpoints for form management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.session import get_session
from auth.service import get_current_user
from auth.models import User
from db.repository import FormRepository
from api.schemas import (
    FormCreate,
    FormUpdate,
    FormResponse,
    FormSubmissionCreate,
    FormSubmissionResponse
)


router = APIRouter(prefix="/forms", tags=["forms"])


@router.post("", response_model=FormResponse)
async def create_form(
    form: FormCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> FormResponse:
    """Create new form.
    
    Args:
        form: Form data
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        FormResponse: Created form
    """
    repo = FormRepository(session)
    created = await repo.create(
        name=form.name,
        schema=form.schema,
        created_by=current_user.id,
        description=form.description
    )
    return FormResponse.model_validate(created)


@router.get("", response_model=List[FormResponse])
async def get_forms(
    active_only: bool = True,
    session: AsyncSession = Depends(get_session)
) -> List[FormResponse]:
    """Get all forms.
    
    Args:
        active_only: Only return active forms
        session: Database session
        
    Returns:
        List[FormResponse]: List of forms
    """
    repo = FormRepository(session)
    if active_only:
        forms = await repo.get_active_forms()
    else:
        forms = await repo.get_all_forms()
    return [FormResponse.model_validate(form) for form in forms]


@router.get("/{form_id}", response_model=FormResponse)
async def get_form(
    form_id: int,
    session: AsyncSession = Depends(get_session)
) -> FormResponse:
    """Get form by ID.
    
    Args:
        form_id: Form ID
        session: Database session
        
    Returns:
        FormResponse: Form if found
        
    Raises:
        HTTPException: If form not found
    """
    repo = FormRepository(session)
    form = await repo.get_by_id(form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    return FormResponse.model_validate(form)


@router.put("/{form_id}", response_model=FormResponse)
async def update_form(
    form_id: int,
    form: FormUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> FormResponse:
    """Update form.
    
    Args:
        form_id: Form ID
        form: Form update data
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        FormResponse: Updated form
        
    Raises:
        HTTPException: If form not found
    """
    repo = FormRepository(session)
    existing = await repo.get_by_id(form_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    
    # Verify ownership or admin status
    if (
        existing.created_by != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this form"
        )
    
    updated = await repo.update(
        form_id,
        **form.model_dump(exclude_unset=True)
    )
    return FormResponse.model_validate(updated)


@router.post(
    "/{form_id}/submit",
    response_model=FormSubmissionResponse
)
async def submit_form(
    form_id: int,
    submission: FormSubmissionCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> FormSubmissionResponse:
    """Submit form response.
    
    Args:
        form_id: Form ID
        submission: Form submission data
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        FormSubmissionResponse: Created submission
        
    Raises:
        HTTPException: If form not found or inactive
    """
    # Verify form exists and is active
    form_repo = FormRepository(session)
    form = await form_repo.get_by_id(form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    
    if not form.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Form is not active"
        )
    
    # Create submission
    from db.repository import FormSubmissionRepository
    repo = FormSubmissionRepository(session)
    created = await repo.create(
        form_id=form_id,
        submitted_by=current_user.id,
        company_id=submission.company_id,
        data=submission.data
    )
    return FormSubmissionResponse.model_validate(created)


@router.get(
    "/{form_id}/submissions",
    response_model=List[FormSubmissionResponse]
)
async def get_form_submissions(
    form_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> List[FormSubmissionResponse]:
    """Get form submissions.
    
    Args:
        form_id: Form ID
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        List[FormSubmissionResponse]: List of submissions
        
    Raises:
        HTTPException: If form not found
    """
    # Verify form exists
    form_repo = FormRepository(session)
    form = await form_repo.get_by_id(form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    
    # Get submissions
    from db.repository import FormSubmissionRepository
    repo = FormSubmissionRepository(session)
    submissions = await repo.get_form_submissions(form_id)
    return [
        FormSubmissionResponse.model_validate(sub)
        for sub in submissions
    ]
