"""User schemas."""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from ...domain.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.USER
    status: Optional[UserStatus] = UserStatus.PENDING
    preferences: Optional[Dict[str, Any]] = None

class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserAdminUpdate(UserUpdate):
    """User admin update schema."""
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    """User response schema."""
    id: UUID
    is_verified: bool
    email_verified_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class UserPreferencesUpdate(BaseModel):
    """User preferences update schema."""
    preferences: Dict[str, Any]
