"""Company endpoints.

This module provides API endpoints for company management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.session import get_session
from auth.service import get_current_user
from auth.models import User
from db.repository import CompanyRepository, CompanyFormRepository
from api.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyFormCreate,
    CompanyFormUpdate,
    CompanyFormResponse
)


router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> CompanyResponse:
    """Create new company.
    
    Args:
        company: Company data
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        CompanyResponse: Created company
        
    Raises:
        HTTPException: If company code already exists
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can create companies"
        )
    
    repo = CompanyRepository(session)
    
    # Check if code exists
    existing = await repo.get_by_code(company.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company code already exists"
        )
    
    created = await repo.create(
        name=company.name,
        code=company.code,
        settings=company.settings
    )
    return CompanyResponse.model_validate(created)


@router.get("", response_model=List[CompanyResponse])
async def get_companies(
    active_only: bool = True,
    session: AsyncSession = Depends(get_session)
) -> List[CompanyResponse]:
    """Get all companies.
    
    Args:
        active_only: Only return active companies
        session: Database session
        
    Returns:
        List[CompanyResponse]: List of companies
    """
    repo = CompanyRepository(session)
    if active_only:
        companies = await repo.get_active_companies()
    else:
        companies = await repo.get_all_companies()
    return [CompanyResponse.model_validate(c) for c in companies]


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    session: AsyncSession = Depends(get_session)
) -> CompanyResponse:
    """Get company by ID.
    
    Args:
        company_id: Company ID
        session: Database session
        
    Returns:
        CompanyResponse: Company if found
        
    Raises:
        HTTPException: If company not found
    """
    repo = CompanyRepository(session)
    company = await repo.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return CompanyResponse.model_validate(company)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> CompanyResponse:
    """Update company.
    
    Args:
        company_id: Company ID
        company: Company update data
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        CompanyResponse: Updated company
        
    Raises:
        HTTPException: If company not found or unauthorized
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can update companies"
        )
    
    repo = CompanyRepository(session)
    existing = await repo.get_by_id(company_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check code uniqueness if changing
    if company.code and company.code != existing.code:
        code_exists = await repo.get_by_code(company.code)
        if code_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company code already exists"
            )
    
    updated = await repo.update(
        company_id,
        **company.model_dump(exclude_unset=True)
    )
    return CompanyResponse.model_validate(updated)


@router.post(
    "/{company_id}/forms",
    response_model=CompanyFormResponse
)
async def assign_form(
    company_id: int,
    form: CompanyFormCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> CompanyFormResponse:
    """Assign form to company.
    
    Args:
        company_id: Company ID
        form: Company form data
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        CompanyFormResponse: Created association
        
    Raises:
        HTTPException: If company or form not found
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can assign forms"
        )
    
    # Verify company exists
    company_repo = CompanyRepository(session)
    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Verify form exists
    from db.repository import FormRepository
    form_repo = FormRepository(session)
    form_exists = await form_repo.get_by_id(form.form_id)
    if not form_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    
    # Create association
    repo = CompanyFormRepository(session)
    created = await repo.create(
        company_id=company_id,
        form_id=form.form_id,
        settings=form.settings
    )
    return CompanyFormResponse.model_validate(created)


@router.get(
    "/{company_id}/forms",
    response_model=List[CompanyFormResponse]
)
async def get_company_forms(
    company_id: int,
    active_only: bool = True,
    session: AsyncSession = Depends(get_session)
) -> List[CompanyFormResponse]:
    """Get forms assigned to company.
    
    Args:
        company_id: Company ID
        active_only: Only return active assignments
        session: Database session
        
    Returns:
        List[CompanyFormResponse]: List of form assignments
        
    Raises:
        HTTPException: If company not found
    """
    # Verify company exists
    company_repo = CompanyRepository(session)
    company = await company_repo.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    repo = CompanyFormRepository(session)
    forms = await repo.get_company_forms(
        company_id,
        active_only=active_only
    )
    return [CompanyFormResponse.model_validate(f) for f in forms]


@router.put(
    "/{company_id}/forms/{form_id}",
    response_model=CompanyFormResponse
)
async def update_form_settings(
    company_id: int,
    form_id: int,
    settings: CompanyFormUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> CompanyFormResponse:
    """Update company-form settings.
    
    Args:
        company_id: Company ID
        form_id: Form ID
        settings: Settings update data
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        CompanyFormResponse: Updated association
        
    Raises:
        HTTPException: If association not found
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can update settings"
        )
    
    repo = CompanyFormRepository(session)
    updated = await repo.update_settings(
        company_id=company_id,
        form_id=form_id,
        settings=settings.settings
    )
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company-form association not found"
        )
    
    return CompanyFormResponse.model_validate(updated)
