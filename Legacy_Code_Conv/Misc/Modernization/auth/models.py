"""
Authentication and authorization models.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class Role(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Permission enumeration."""
    # Deposit permissions
    DEPOSIT_CREATE = "deposit:create"
    DEPOSIT_READ = "deposit:read"
    DEPOSIT_UPDATE = "deposit:update"
    DEPOSIT_DELETE = "deposit:delete"
    
    # Void permissions
    VOID_CREATE = "void:create"
    VOID_READ = "void:read"
    VOID_UPDATE = "void:update"
    VOID_PROCESS = "void:process"
    
    # Purchase order permissions
    PO_CREATE = "po:create"
    PO_READ = "po:read"
    PO_UPDATE = "po:update"
    PO_RECEIVE = "po:receive"


class RolePermissions:
    """Role to permission mappings."""
    MAPPINGS = {
        Role.ADMIN: [p.value for p in Permission],
        Role.MANAGER: [
            Permission.DEPOSIT_CREATE.value,
            Permission.DEPOSIT_READ.value,
            Permission.DEPOSIT_UPDATE.value,
            Permission.VOID_CREATE.value,
            Permission.VOID_READ.value,
            Permission.VOID_PROCESS.value,
            Permission.PO_CREATE.value,
            Permission.PO_READ.value,
            Permission.PO_UPDATE.value,
            Permission.PO_RECEIVE.value
        ],
        Role.OPERATOR: [
            Permission.DEPOSIT_CREATE.value,
            Permission.DEPOSIT_READ.value,
            Permission.VOID_CREATE.value,
            Permission.VOID_READ.value,
            Permission.PO_READ.value,
            Permission.PO_RECEIVE.value
        ],
        Role.VIEWER: [
            Permission.DEPOSIT_READ.value,
            Permission.VOID_READ.value,
            Permission.PO_READ.value
        ]
    }


class Token(BaseModel):
    """Token model."""
    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    token_type: str = Field(
        "bearer",
        description="Token type"
    )
    expires_in: int = Field(
        ...,
        description="Token expiration in seconds"
    )


class TokenData(BaseModel):
    """Token data model."""
    username: str = Field(..., description="Username")
    role: Role = Field(..., description="User role")
    permissions: List[str] = Field(
        ...,
        description="User permissions"
    )
    exp: datetime = Field(..., description="Expiration time")


class User(BaseModel):
    """User model."""
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    role: Role = Field(..., description="User role")
    is_active: bool = Field(
        True,
        description="Whether user is active"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Update timestamp"
    )


class UserInDB(User):
    """Database user model."""
    hashed_password: str = Field(
        ...,
        description="Hashed password"
    )
