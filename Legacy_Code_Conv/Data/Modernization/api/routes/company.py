"""Company API routes."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user, get_unit_of_work
from core.models.company import Company
from core.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from infrastructure.data.unit_of_work import UnitOfWork
from infrastructure.repositories.company import CompanyRepository

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get(
    "/",
    response_model=List[CompanyResponse],
    summary="List Companies",
    description="""
    Retrieve a list of all active companies.
    
    This endpoint supports pagination and filtering by:
    - Name (partial match)
    - NPI (exact match)
    - Active status
    
    Results are ordered by company name by default.
    """,
    response_description="List of company objects"
)
async def list_companies(
    name: str = Query(None, description="Filter by company name (partial match)"),
    npi: str = Query(None, description="Filter by NPI number (exact match)"),
    is_active: bool = Query(True, description="Filter by active status"),
    offset: int = Query(0, description="Number of records to skip"),
    limit: int = Query(10, description="Maximum number of records to return"),
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all companies with filtering and pagination.
    
    Args:
        name: Optional company name filter
        npi: Optional NPI number filter
        is_active: Filter by active status
        offset: Number of records to skip
        limit: Maximum number of records to return
        session: Database session
        current_user: Current user info
        
    Returns:
        List of companies matching the filters
    """
    repo = CompanyRepository(session)
    companies = await repo.get_active_companies(
        name=name,
        npi=npi,
        is_active=is_active,
        offset=offset,
        limit=limit
    )
    return [CompanyResponse.from_orm(c) for c in companies]

@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=201,
    summary="Create Company",
    description="""
    Create a new company.
    
    Required fields:
    - name: Company name
    - npi: National Provider Identifier
    - tax_id: Tax ID number
    
    The NPI must be unique across all companies.
    """,
    response_description="Created company object",
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Company with this NPI already exists",
                        "code": "DUPLICATE_NPI"
                    }
                }
            }
        }
    }
)
async def create_company(
    company: CompanyCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: dict = Depends(get_current_user)
):
    """Create new company.
    
    Args:
        company: Company data
        uow: Unit of work
        current_user: Current user info
        
    Returns:
        Created company
        
    Raises:
        HTTPException: If company with NPI already exists
    """
    async with uow:
        repo = uow.get_repository(Company)
        
        # Check if company with NPI exists
        existing = await repo.get_by_npi(company.npi)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Company with this NPI already exists"
            )
        
        # Create company
        new_company = Company(**company.dict())
        await repo.add(new_company)
        
        return CompanyResponse.from_orm(new_company)

@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get Company",
    description="""
    Retrieve a specific company by ID.
    
    The company ID must be a valid UUID.
    Returns 404 if company is not found.
    """,
    response_description="Company object",
    responses={
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Company not found",
                        "code": "NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def get_company(
    company_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get company by ID.
    
    Args:
        company_id: Company ID
        session: Database session
        current_user: Current user info
        
    Returns:
        Company details
        
    Raises:
        HTTPException: If company not found
    """
    repo = CompanyRepository(session)
    company = await repo.get_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    return CompanyResponse.from_orm(company)

@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Update Company",
    description="""
    Update an existing company.
    
    Only provided fields will be updated.
    Returns 404 if company is not found.
    """,
    response_description="Updated company object",
    responses={
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Company not found",
                        "code": "NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def update_company(
    company_id: UUID,
    company_update: CompanyUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: dict = Depends(get_current_user)
):
    """Update company.
    
    Args:
        company_id: Company ID
        company_update: Updated company data
        uow: Unit of work
        current_user: Current user info
        
    Returns:
        Updated company
        
    Raises:
        HTTPException: If company not found
    """
    async with uow:
        repo = uow.get_repository(Company)
        company = await repo.get_by_id(company_id)
        
        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )
        
        # Update company fields
        for field, value in company_update.dict(exclude_unset=True).items():
            setattr(company, field, value)
        
        await repo.update(company)
        return CompanyResponse.from_orm(company)

@router.delete(
    "/{company_id}",
    status_code=204,
    summary="Delete Company",
    description="""
    Soft delete a company.
    
    This operation marks the company as deleted but does not remove it from the database.
    Returns 404 if company is not found.
    """,
    responses={
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Company not found",
                        "code": "NOT_FOUND"
                    }
                }
            }
        }
    }
)
async def delete_company(
    company_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: dict = Depends(get_current_user)
):
    """Delete company.
    
    Args:
        company_id: Company ID
        uow: Unit of work
        current_user: Current user info
        
    Raises:
        HTTPException: If company not found
    """
    async with uow:
        repo = uow.get_repository(Company)
        company = await repo.get_by_id(company_id)
        
        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )
        
        await repo.soft_delete(company_id)
