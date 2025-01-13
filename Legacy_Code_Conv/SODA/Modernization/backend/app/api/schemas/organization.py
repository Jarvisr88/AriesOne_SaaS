"""Organization schemas."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from ...domain.models.organization import OrganizationType, OrganizationStatus

class OrganizationBase(BaseModel):
    """Base organization schema."""
    name: str
    code: str = Field(..., regex="^[A-Za-z0-9]+$")
    type: OrganizationType
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class OrganizationCreate(OrganizationBase):
    """Organization creation schema."""
    parent_id: Optional[UUID] = None

class OrganizationUpdate(BaseModel):
    """Organization update schema."""
    name: Optional[str] = None
    code: Optional[str] = Field(None, regex="^[A-Za-z0-9]+$")
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class OrganizationResponse(OrganizationBase):
    """Organization response schema."""
    id: UUID
    parent_id: Optional[UUID] = None
    status: OrganizationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: UUID
    updated_by_id: Optional[UUID] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class OrganizationSettingsUpdate(BaseModel):
    """Organization settings update schema."""
    settings: Dict[str, Any]

class UserOrganizationBase(BaseModel):
    """Base user organization schema."""
    role: str
    permissions: Optional[Dict[str, Any]] = None

class UserOrganizationCreate(UserOrganizationBase):
    """User organization creation schema."""
    user_id: UUID

class UserOrganizationUpdate(UserOrganizationBase):
    """User organization update schema."""
    pass

class UserOrganizationResponse(UserOrganizationBase):
    """User organization response schema."""
    organization_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class OrganizationWithUsers(OrganizationResponse):
    """Organization response with users schema."""
    users: List[UserOrganizationResponse]
