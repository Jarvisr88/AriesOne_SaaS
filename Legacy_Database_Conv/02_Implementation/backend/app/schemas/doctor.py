"""
Doctor/Provider Pydantic schemas for AriesOne SaaS application.
Defines data validation and serialization for doctor-related entities.
"""
from datetime import datetime, date
from typing import Optional, List, Set
from pydantic import BaseModel, Field

# Doctor Type Schemas

class DoctorTypeBase(BaseModel):
    """Base schema for doctor types."""
    name: str

class DoctorTypeCreate(DoctorTypeBase):
    """Schema for creating a doctor type."""
    created_by_id: Optional[int] = None
    last_update_user_id: Optional[int] = None

class DoctorTypeUpdate(DoctorTypeBase):
    """Schema for updating a doctor type."""
    name: Optional[str] = None
    last_update_user_id: Optional[int] = None

# Doctor Schemas

class DoctorBase(BaseModel):
    """Base schema for doctors."""
    type_id: Optional[int] = None
    courtesy: str = Field(..., regex="^(Dr.|Miss|Mr.|Mrs.|Rev.)$")
    first_name: str = Field(..., max_length=25)
    middle_name: str = Field(..., max_length=1)
    last_name: str = Field(..., max_length=30)
    suffix: str = Field(..., max_length=4)
    title: str = Field(..., max_length=50)
    address1: str = Field(..., max_length=40)
    address2: str = Field("", max_length=40)
    city: str = Field(..., max_length=25)
    state: str = Field(..., max_length=2)
    zip: str = Field(..., max_length=10)
    phone: str = Field(..., max_length=50)
    phone2: str = Field("", max_length=50)
    fax: str = Field("", max_length=50)
    contact: str = Field("", max_length=50)
    npi: Optional[str] = Field(None, max_length=10)
    upin_number: str = Field(..., max_length=11)
    license_number: str = Field(..., max_length=16)
    license_expired: Optional[date] = None
    medicaid_number: str = Field(..., max_length=16)
    fed_tax_id: str = Field(..., max_length=9)
    dea_number: str = Field("", max_length=20)
    other_id: str = Field("", max_length=16)
    pecos_enrolled: bool = False
    mir: Set[str] = Field(default_factory=set)

class DoctorCreate(DoctorBase):
    """Schema for creating a doctor."""
    created_by_id: Optional[int] = None
    last_update_user_id: Optional[int] = None

class DoctorUpdate(DoctorBase):
    """Schema for updating a doctor."""
    type_id: Optional[int] = None
    courtesy: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix: Optional[str] = None
    title: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    phone: Optional[str] = None
    phone2: Optional[str] = None
    fax: Optional[str] = None
    contact: Optional[str] = None
    npi: Optional[str] = None
    upin_number: Optional[str] = None
    license_number: Optional[str] = None
    license_expired: Optional[date] = None
    medicaid_number: Optional[str] = None
    fed_tax_id: Optional[str] = None
    dea_number: Optional[str] = None
    other_id: Optional[str] = None
    pecos_enrolled: Optional[bool] = None
    mir: Optional[Set[str]] = None
    last_update_user_id: Optional[int] = None

# Provider Number Type Schemas

class ProviderNumberTypeBase(BaseModel):
    """Base schema for provider number types."""
    name: str
    description: Optional[str] = None

class ProviderNumberTypeCreate(ProviderNumberTypeBase):
    """Schema for creating a provider number type."""
    created_by_id: Optional[int] = None
    last_update_user_id: Optional[int] = None

class ProviderNumberTypeUpdate(ProviderNumberTypeBase):
    """Schema for updating a provider number type."""
    name: Optional[str] = None
    description: Optional[str] = None
    last_update_user_id: Optional[int] = None

# Provider Number Schemas

class ProviderNumberBase(BaseModel):
    """Base schema for provider numbers."""
    doctor_id: int
    type_id: int
    number: str = Field(..., max_length=50)
    expiration_date: Optional[date] = None
    is_active: bool = True
    notes: Optional[str] = None

class ProviderNumberCreate(ProviderNumberBase):
    """Schema for creating a provider number."""
    created_by_id: Optional[int] = None
    last_update_user_id: Optional[int] = None

class ProviderNumberUpdate(ProviderNumberBase):
    """Schema for updating a provider number."""
    type_id: Optional[int] = None
    number: Optional[str] = None
    expiration_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    last_update_user_id: Optional[int] = None

# Response Schemas

class UserRef(BaseModel):
    """Reference to a user."""
    id: int
    username: str

    class Config:
        orm_mode = True

class DoctorTypeResponse(DoctorTypeBase):
    """Response schema for doctor types."""
    id: int
    created_datetime: datetime
    last_update_datetime: datetime
    created_by: UserRef
    last_update_user: UserRef

    class Config:
        orm_mode = True

class ProviderNumberTypeResponse(ProviderNumberTypeBase):
    """Response schema for provider number types."""
    id: int
    created_datetime: datetime
    last_update_datetime: datetime
    created_by: UserRef
    last_update_user: UserRef

    class Config:
        orm_mode = True

class ProviderNumberResponse(ProviderNumberBase):
    """Response schema for provider numbers."""
    id: int
    number_type: ProviderNumberTypeResponse
    created_datetime: datetime
    last_update_datetime: datetime
    created_by: UserRef
    last_update_user: UserRef

    class Config:
        orm_mode = True

class DoctorResponse(DoctorBase):
    """Response schema for doctors."""
    id: int
    doctor_type: Optional[DoctorTypeResponse] = None
    provider_numbers: List[ProviderNumberResponse] = []
    created_datetime: datetime
    last_update_datetime: datetime
    created_by: UserRef
    last_update_user: UserRef

    class Config:
        orm_mode = True
