"""
Pydantic schemas for company domain.
Provides request and response validation for company-related operations.
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, constr, EmailStr, Field, validator

from ..models.company import OrganizationStatus, EmployeeStatus

# Base schemas
class OrganizationalUnitBase(BaseModel):
    """Base schema for organizational units."""
    name: constr(min_length=1, max_length=100)
    code: constr(min_length=1, max_length=20)
    status: OrganizationStatus = OrganizationStatus.ACTIVE
    phone: Optional[constr(max_length=20)] = None
    email: Optional[EmailStr] = None
    website: Optional[constr(max_length=200)] = None
    effective_start_date: date = Field(default_factory=date.today)
    effective_end_date: Optional[date] = None
    description: Optional[constr(max_length=500)] = None
    internal_notes: Optional[constr(max_length=500)] = None

    @validator('effective_end_date')
    def end_date_after_start_date(cls, v, values):
        """Validate end date is after start date."""
        if v and values.get('effective_start_date') and v <= values['effective_start_date']:
            raise ValueError('end_date must be after start_date')
        return v

# Company schemas
class CompanyBase(OrganizationalUnitBase):
    """Base schema for companies."""
    tax_id: Optional[constr(max_length=20)] = None
    dme_license_number: Optional[constr(max_length=50)] = None
    npi_number: Optional[constr(max_length=10)] = None
    address_line1: constr(min_length=1, max_length=100)
    address_line2: Optional[constr(max_length=100)] = None
    city: constr(min_length=1, max_length=100)
    state: constr(min_length=2, max_length=2)
    zip_code: constr(min_length=5, max_length=10)
    country: constr(min_length=2, max_length=2) = "US"
    fiscal_year_start: int = Field(1, ge=1, le=12)
    time_zone: str = "America/Chicago"
    currency: str = "USD"

class CompanyCreate(CompanyBase):
    """Schema for creating companies."""
    pass

class CompanyUpdate(BaseModel):
    """Schema for updating companies."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    status: Optional[OrganizationStatus] = None
    phone: Optional[constr(max_length=20)] = None
    email: Optional[EmailStr] = None
    website: Optional[constr(max_length=200)] = None
    tax_id: Optional[constr(max_length=20)] = None
    dme_license_number: Optional[constr(max_length=50)] = None
    npi_number: Optional[constr(max_length=10)] = None
    address_line1: Optional[constr(min_length=1, max_length=100)] = None
    address_line2: Optional[constr(max_length=100)] = None
    city: Optional[constr(min_length=1, max_length=100)] = None
    state: Optional[constr(min_length=2, max_length=2)] = None
    zip_code: Optional[constr(min_length=5, max_length=10)] = None
    fiscal_year_start: Optional[int] = Field(None, ge=1, le=12)
    time_zone: Optional[str] = None
    currency: Optional[str] = None

class CompanyResponse(CompanyBase):
    """Schema for company responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Location schemas
class LocationBase(OrganizationalUnitBase):
    """Base schema for locations."""
    company_id: int
    address_line1: constr(min_length=1, max_length=100)
    address_line2: Optional[constr(max_length=100)] = None
    city: constr(min_length=1, max_length=100)
    state: constr(min_length=2, max_length=2)
    zip_code: constr(min_length=5, max_length=10)
    country: constr(min_length=2, max_length=2) = "US"
    is_warehouse: bool = False
    is_service_center: bool = False
    service_radius: Optional[int] = None
    operating_hours: Optional[str] = None
    local_license_number: Optional[constr(max_length=50)] = None
    license_expiry_date: Optional[date] = None

class LocationCreate(LocationBase):
    """Schema for creating locations."""
    pass

class LocationUpdate(BaseModel):
    """Schema for updating locations."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    status: Optional[OrganizationStatus] = None
    phone: Optional[constr(max_length=20)] = None
    email: Optional[EmailStr] = None
    address_line1: Optional[constr(min_length=1, max_length=100)] = None
    address_line2: Optional[constr(max_length=100)] = None
    city: Optional[constr(min_length=1, max_length=100)] = None
    state: Optional[constr(min_length=2, max_length=2)] = None
    zip_code: Optional[constr(min_length=5, max_length=10)] = None
    is_warehouse: Optional[bool] = None
    is_service_center: Optional[bool] = None
    service_radius: Optional[int] = None
    operating_hours: Optional[str] = None
    local_license_number: Optional[constr(max_length=50)] = None
    license_expiry_date: Optional[date] = None

class LocationResponse(LocationBase):
    """Schema for location responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Department schemas
class DepartmentBase(OrganizationalUnitBase):
    """Base schema for departments."""
    company_id: int
    location_id: Optional[int] = None
    parent_department_id: Optional[int] = None
    department_type: Optional[str] = None
    cost_center: Optional[constr(max_length=20)] = None
    budget_code: Optional[constr(max_length=20)] = None

class DepartmentCreate(DepartmentBase):
    """Schema for creating departments."""
    pass

class DepartmentUpdate(BaseModel):
    """Schema for updating departments."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    status: Optional[OrganizationStatus] = None
    location_id: Optional[int] = None
    parent_department_id: Optional[int] = None
    department_type: Optional[str] = None
    cost_center: Optional[constr(max_length=20)] = None
    budget_code: Optional[constr(max_length=20)] = None

class DepartmentResponse(DepartmentBase):
    """Schema for department responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime
    child_departments: List['DepartmentResponse'] = []

    class Config:
        from_attributes = True

# Employee schemas
class EmployeeBase(BaseModel):
    """Base schema for employees."""
    employee_number: constr(min_length=1, max_length=20)
    company_id: int
    location_id: Optional[int] = None
    department_id: Optional[int] = None
    user_id: Optional[int] = None
    first_name: constr(min_length=1, max_length=50)
    middle_name: Optional[constr(max_length=50)] = None
    last_name: constr(min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[constr(max_length=20)] = None
    hire_date: date
    termination_date: Optional[date] = None
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    is_full_time: bool = True
    title: Optional[constr(max_length=100)] = None
    license_number: Optional[constr(max_length=50)] = None
    license_expiry_date: Optional[date] = None
    certifications: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    """Schema for creating employees."""
    role_ids: List[int] = []

class EmployeeUpdate(BaseModel):
    """Schema for updating employees."""
    location_id: Optional[int] = None
    department_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[constr(max_length=20)] = None
    termination_date: Optional[date] = None
    status: Optional[EmployeeStatus] = None
    is_full_time: Optional[bool] = None
    title: Optional[constr(max_length=100)] = None
    license_number: Optional[constr(max_length=50)] = None
    license_expiry_date: Optional[date] = None
    certifications: Optional[str] = None
    role_ids: Optional[List[int]] = None

class EmployeeResponse(EmployeeBase):
    """Schema for employee responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime
    roles: List['RoleResponse'] = []

    class Config:
        from_attributes = True

# Role schemas
class RoleBase(BaseModel):
    """Base schema for roles."""
    name: constr(min_length=1, max_length=50)
    code: constr(min_length=1, max_length=20)
    description: Optional[constr(max_length=200)] = None
    is_system_role: bool = False
    permissions: Optional[str] = None

class RoleCreate(RoleBase):
    """Schema for creating roles."""
    pass

class RoleUpdate(BaseModel):
    """Schema for updating roles."""
    name: Optional[constr(min_length=1, max_length=50)] = None
    description: Optional[constr(max_length=200)] = None
    permissions: Optional[str] = None

class RoleResponse(RoleBase):
    """Schema for role responses."""
    id: int
    created_by_id: int
    created_datetime: datetime
    last_update_user_id: Optional[int] = None
    last_update_datetime: datetime

    class Config:
        from_attributes = True

# Update forward references
DepartmentResponse.update_forward_refs()
EmployeeResponse.update_forward_refs()
