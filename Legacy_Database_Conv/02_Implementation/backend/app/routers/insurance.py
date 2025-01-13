"""
Insurance API router for AriesOne SaaS application.
Implements REST endpoints for insurance processing and eligibility verification.
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..services.insurance import InsuranceService, CustomerInsuranceService, EligibilityService
from ..models.insurance import InsuranceType, EligibilityStatus
from ..schemas.insurance import (
    InsuranceCompanyCreate, InsuranceCompanyUpdate, InsuranceCompanyResponse,
    InsuranceGroupCreate, InsuranceGroupResponse,
    CustomerInsuranceCreate, CustomerInsuranceUpdate, CustomerInsuranceResponse,
    EligibilityRequestCreate, EligibilityRequestUpdate, EligibilityRequestResponse,
    EligibilityCheckRequest, EligibilityCheckResponse
)
from ..dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/v1/insurance",
    tags=["insurance"]
)

# Insurance Company Routes

@router.get("/companies", response_model=List[InsuranceCompanyResponse])
async def list_companies(
    type: Optional[InsuranceType] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List insurance companies with optional filtering."""
    service = InsuranceService(db)
    companies = service.get_active_companies()
    if type:
        companies = [c for c in companies if c.insurance_type == type]
    return companies

@router.get("/companies/{company_id}", response_model=InsuranceCompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific insurance company by ID."""
    service = InsuranceService(db)
    company = service.get_company_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance company not found"
        )
    return company

@router.post("/companies", response_model=InsuranceCompanyResponse)
async def create_company(
    company_data: InsuranceCompanyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new insurance company."""
    service = InsuranceService(db)
    company_data.created_by_id = current_user.id
    company_data.last_update_user_id = current_user.id
    return service.create_company(company_data.dict())

@router.put("/companies/{company_id}", response_model=InsuranceCompanyResponse)
async def update_company(
    company_id: int,
    company_data: InsuranceCompanyUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing insurance company."""
    service = InsuranceService(db)
    company_data.last_update_user_id = current_user.id
    company = service.update_company(company_id, company_data.dict(exclude_unset=True))
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance company not found"
        )
    return company

# Customer Insurance Routes

@router.get("/customer/{customer_id}/policies", response_model=List[CustomerInsuranceResponse])
async def list_customer_policies(
    customer_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List insurance policies for a customer."""
    service = CustomerInsuranceService(db)
    return service.get_customer_insurances(customer_id)

@router.post("/customer/policies", response_model=CustomerInsuranceResponse)
async def create_customer_policy(
    policy_data: CustomerInsuranceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new customer insurance policy."""
    service = CustomerInsuranceService(db)
    policy_data.created_by_id = current_user.id
    policy_data.last_update_user_id = current_user.id
    return service.create_insurance(policy_data.dict())

@router.put("/customer/policies/{policy_id}", response_model=CustomerInsuranceResponse)
async def update_customer_policy(
    policy_id: int,
    policy_data: CustomerInsuranceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing customer insurance policy."""
    service = CustomerInsuranceService(db)
    policy_data.last_update_user_id = current_user.id
    policy = service.update_insurance(policy_id, policy_data.dict(exclude_unset=True))
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance policy not found"
        )
    return policy

# Eligibility Routes

@router.post("/eligibility/check", response_model=EligibilityCheckResponse)
async def check_eligibility(
    check_data: EligibilityCheckRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Check insurance eligibility for a service."""
    service = EligibilityService(db)
    result = service.check_eligibility(
        check_data.insurance_id,
        check_data.service_type,
        check_data.service_date
    )
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    return result

@router.get("/eligibility/requests/{request_id}", response_model=EligibilityRequestResponse)
async def get_eligibility_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific eligibility request by ID."""
    service = EligibilityService(db)
    request = service.get_request_by_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Eligibility request not found"
        )
    return request

@router.get("/customer/policies/{policy_id}/eligibility", response_model=List[EligibilityRequestResponse])
async def list_eligibility_requests(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List eligibility requests for a customer insurance policy."""
    service = EligibilityService(db)
    return service.get_requests_by_insurance(policy_id)
