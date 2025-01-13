"""Company schema module."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, constr

class CompanyBase(BaseModel):
    """Base schema for Company data."""
    
    name: str
    tax_id: constr(regex=r'^\d{2}-\d{7}$')
    npi: constr(regex=r'^\d{10}$')
    is_active: bool = True
    license_expiry: Optional[datetime] = None
    address: Optional[str] = None
    phone: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None

class CompanyCreate(CompanyBase):
    """Schema for creating a Company."""
    pass

class CompanyUpdate(CompanyBase):
    """Schema for updating a Company."""
    name: Optional[str] = None
    tax_id: Optional[constr(regex=r'^\d{2}-\d{7}$')] = None
    npi: Optional[constr(regex=r'^\d{10}$')] = None
    is_active: Optional[bool] = None

class CompanyInDB(CompanyBase):
    """Schema for Company data from database."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime]

    class Config:
        """Pydantic configuration."""
        from_attributes = True
