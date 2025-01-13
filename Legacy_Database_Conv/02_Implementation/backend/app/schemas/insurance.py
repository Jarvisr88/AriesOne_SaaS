"""
Insurance Pydantic schemas for AriesOne SaaS application.
Defines data validation and serialization for insurance-related entities.
"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal

from ..models.insurance import InsuranceType, EligibilityStatus

# Insurance Company Schemas

class InsuranceCompanyBase(BaseModel):
    """Base schema for insurance companies."""
    name: str
    group_id: Optional[int] = None
    insurance_type: InsuranceType
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    medicare_number: Optional[str] = None
    medicaid_number: Optional[str] = None
    office_ally_number: Optional[str] = None
    zirmed_number: Optional[str] = None
    availity_number: Optional[str] = None
    ability_number: Optional[str] = None
    ability_eligibility_payer_id: Optional[str] = None
    expected_percent: Optional[Decimal] = None
    price_code_id: Optional[int] = None
    print_hao_on_invoice: bool = False
    print_inv_on_invoice: bool = False
    invoice_form_id: Optional[int] = None
    is_active: bool = True

class InsuranceCompanyCreate(InsuranceCompanyBase):
    """Schema for creating an insurance company."""
    created_by_id: Optional[int] = None
    last_update_user_id: Optional[int] = None

class InsuranceCompanyUpdate(InsuranceCompanyBase):
    """Schema for updating an insurance company."""
    name: Optional[str] = None
    insurance_type: Optional[InsuranceType] = None
    last_update_user_id: Optional[int] = None

class InsuranceGroupBase(BaseModel):
    """Base schema for insurance company groups."""
    name: str

class InsuranceGroupCreate(InsuranceGroupBase):
    """Schema for creating an insurance company group."""
    created_by_id: Optional[int] = None
    last_update_user_id: Optional[int] = None

class InsuranceGroupUpdate(InsuranceGroupBase):
    """Schema for updating an insurance company group."""
    name: Optional[str] = None
    last_update_user_id: Optional[int] = None

# Customer Insurance Schemas

class CustomerInsuranceBase(BaseModel):
    """Base schema for customer insurance policies."""
    customer_id: int
    company_id: int
    priority: int = 1
    policy_number: str
    group_number: Optional[str] = None
    subscriber_id: Optional[str] = None
    relationship_to_subscriber: Optional[str] = None
    effective_date: date
    termination_date: Optional[date] = None
    last_verified_date: Optional[date] = None
    verification_status: EligibilityStatus = EligibilityStatus.PENDING
    verification_notes: Optional[str] = None
    authorization_required: bool = False
    authorization_number: Optional[str] = None
    authorization_start_date: Optional[date] = None
    authorization_end_date: Optional[date] = None
    authorization_notes: Optional[str] = None
    is_active: bool = True

class CustomerInsuranceCreate(CustomerInsuranceBase):
    """Schema for creating a customer insurance policy."""
    created_by_id: Optional[int] = None
    last_update_user_id: Optional[int] = None

class CustomerInsuranceUpdate(CustomerInsuranceBase):
    """Schema for updating a customer insurance policy."""
    company_id: Optional[int] = None
    priority: Optional[int] = None
    policy_number: Optional[str] = None
    effective_date: Optional[date] = None
    last_update_user_id: Optional[int] = None

# Eligibility Request Schemas

class EligibilityRequestBase(BaseModel):
    """Base schema for eligibility verification requests."""
    customer_insurance_id: int
    request_type: str
    service_type: Optional[str] = None
    service_date: Optional[date] = None
    provider_npi: Optional[str] = None
    request_payload: Optional[str] = None

class EligibilityRequestCreate(EligibilityRequestBase):
    """Schema for creating an eligibility request."""
    created_by_id: Optional[int] = None
    last_update_user_id: Optional[int] = None

class EligibilityRequestUpdate(BaseModel):
    """Schema for updating an eligibility request with response data."""
    response_date: datetime
    response_status: EligibilityStatus
    response_code: Optional[str] = None
    response_message: Optional[str] = None
    coverage_status: Optional[str] = None
    coverage_start_date: Optional[date] = None
    coverage_end_date: Optional[date] = None
    deductible_amount: Optional[Decimal] = None
    deductible_met: Optional[Decimal] = None
    out_of_pocket_amount: Optional[Decimal] = None
    out_of_pocket_met: Optional[Decimal] = None
    response_payload: Optional[str] = None
    last_update_user_id: Optional[int] = None

class EligibilityCheckRequest(BaseModel):
    """Schema for checking eligibility."""
    insurance_id: int
    service_type: str
    service_date: date

# Response Schemas

class UserRef(BaseModel):
    """Reference to a user."""
    id: int
    username: str

    class Config:
        orm_mode = True

class InsuranceCompanyResponse(InsuranceCompanyBase):
    """Response schema for insurance companies."""
    id: int
    created_datetime: datetime
    last_update_datetime: datetime
    created_by: UserRef
    last_update_user: UserRef

    class Config:
        orm_mode = True

class InsuranceGroupResponse(InsuranceGroupBase):
    """Response schema for insurance company groups."""
    id: int
    created_datetime: datetime
    last_update_datetime: datetime
    created_by: UserRef
    last_update_user: UserRef

    class Config:
        orm_mode = True

class CustomerInsuranceResponse(CustomerInsuranceBase):
    """Response schema for customer insurance policies."""
    id: int
    created_datetime: datetime
    last_update_datetime: datetime
    company: InsuranceCompanyResponse
    created_by: UserRef
    last_update_user: UserRef

    class Config:
        orm_mode = True

class EligibilityRequestResponse(EligibilityRequestBase):
    """Response schema for eligibility requests."""
    id: int
    response_date: Optional[datetime] = None
    response_status: Optional[EligibilityStatus] = None
    response_code: Optional[str] = None
    response_message: Optional[str] = None
    coverage_status: Optional[str] = None
    coverage_start_date: Optional[date] = None
    coverage_end_date: Optional[date] = None
    deductible_amount: Optional[Decimal] = None
    deductible_met: Optional[Decimal] = None
    out_of_pocket_amount: Optional[Decimal] = None
    out_of_pocket_met: Optional[Decimal] = None
    created_datetime: datetime
    last_update_datetime: datetime
    created_by: UserRef
    last_update_user: UserRef

    class Config:
        orm_mode = True

class EligibilityCheckResponse(BaseModel):
    """Response schema for eligibility checks."""
    status: EligibilityStatus
    coverage_status: Optional[str] = None
    coverage_start_date: Optional[date] = None
    coverage_end_date: Optional[date] = None
    deductible_amount: Optional[Decimal] = None
    deductible_met: Optional[Decimal] = None
    out_of_pocket_amount: Optional[Decimal] = None
    out_of_pocket_met: Optional[Decimal] = None
    message: Optional[str] = None
