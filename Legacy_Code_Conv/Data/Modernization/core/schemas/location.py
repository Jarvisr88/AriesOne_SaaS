"""Location schema module."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, constr

class LocationBase(BaseModel):
    """Base schema for Location data."""
    
    company_id: UUID
    name: str
    address: str
    city: str
    state: constr(regex=r'^[A-Z]{2}$')
    zip_code: constr(regex=r'^\d{5}(-\d{4})?$')
    is_active: bool = True
    phone: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    fax: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    email: Optional[EmailStr] = None

class LocationCreate(LocationBase):
    """Schema for creating a Location."""
    pass

class LocationUpdate(LocationBase):
    """Schema for updating a Location."""
    company_id: Optional[UUID] = None
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[constr(regex=r'^[A-Z]{2}$')] = None
    zip_code: Optional[constr(regex=r'^\d{5}(-\d{4})?$')] = None
    is_active: Optional[bool] = None

class LocationInDB(LocationBase):
    """Schema for Location data from database."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime]

    class Config:
        """Pydantic configuration."""
        from_attributes = True
