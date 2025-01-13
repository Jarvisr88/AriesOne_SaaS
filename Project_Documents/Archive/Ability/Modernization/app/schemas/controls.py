from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.models.access_control import ResourceType

# Permission schemas
class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    resource_type: ResourceType
    action: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None

class PermissionResponse(PermissionBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Role schemas
class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_system_role: bool = False
    parent_role_id: Optional[int] = None
    settings: Dict[str, Any] = Field(default_factory=dict)

class RoleCreate(RoleBase):
    permission_ids: List[int] = Field(default_factory=list)

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None
    settings: Optional[Dict[str, Any]] = None

class RoleResponse(RoleBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse]

    class Config:
        orm_mode = True

# Group schemas
class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_system_group: bool = False
    parent_group_id: Optional[int] = None
    settings: Dict[str, Any] = Field(default_factory=dict)

class GroupCreate(GroupBase):
    role_ids: List[int] = Field(default_factory=list)

class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    role_ids: Optional[List[int]] = None
    settings: Optional[Dict[str, Any]] = None

class GroupResponse(GroupBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse]

    class Config:
        orm_mode = True

# Security Policy schemas
class SecurityPolicyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    policy_type: str = Field(..., min_length=1, max_length=50)
    settings: Dict[str, Any] = Field(...)
    is_enabled: bool = True
    priority: int = 0

    @validator('policy_type')
    def validate_policy_type(cls, v):
        allowed_types = {'password', 'session', 'rate-limit'}
        if v not in allowed_types:
            raise ValueError(f'policy_type must be one of: {allowed_types}')
        return v

class SecurityPolicyCreate(SecurityPolicyBase):
    pass

class SecurityPolicyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None
    priority: Optional[int] = None

class SecurityPolicyResponse(SecurityPolicyBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Audit Log schemas
class AuditLogFilter(BaseModel):
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[int] = None
    actor_id: Optional[int] = None
    action: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    actor_id: int
    action: str
    resource_type: ResourceType
    resource_id: int
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    company_id: int

    class Config:
        orm_mode = True
