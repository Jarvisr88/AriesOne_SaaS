"""
Authentication models for the Core module.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, constr

from ..models.base import BaseDBModel, BaseSchema

# Many-to-many relationship tables
user_roles = Table(
    'core_user_roles',
    BaseDBModel.metadata,
    Column('user_id', Integer, ForeignKey('core_users.id')),
    Column('role_id', Integer, ForeignKey('core_roles.id'))
)

role_permissions = Table(
    'core_role_permissions',
    BaseDBModel.metadata,
    Column('role_id', Integer, ForeignKey('core_roles.id')),
    Column('permission_id', Integer, ForeignKey('core_permissions.id'))
)

class User(BaseDBModel):
    """User model."""
    __tablename__ = 'core_users'

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime)
    roles = relationship('Role', secondary=user_roles, back_populates='users')

class Role(BaseDBModel):
    """Role model."""
    __tablename__ = 'core_roles'

    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    is_system_role = Column(Boolean, default=False)
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')

class Permission(BaseDBModel):
    """Permission model."""
    __tablename__ = 'core_permissions'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(200))
    resource = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')

class Token(BaseDBModel):
    """Token model for JWT tokens."""
    __tablename__ = 'core_tokens'

    user_id = Column(Integer, ForeignKey('core_users.id'), nullable=False)
    token = Column(String(500), nullable=False)
    token_type = Column(String(50), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    device_info = Column(String(200))

# Pydantic Schemas

class UserCreate(BaseModel):
    """Schema for user creation."""
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    """Schema for user update."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(BaseSchema):
    """Schema for user in database."""
    username: str
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime]
    roles: List[str]

class RoleCreate(BaseModel):
    """Schema for role creation."""
    name: constr(min_length=3, max_length=50)
    description: Optional[str] = None
    permissions: List[str] = []

class RoleUpdate(BaseModel):
    """Schema for role update."""
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class RoleInDB(BaseSchema):
    """Schema for role in database."""
    name: str
    description: Optional[str]
    is_system_role: bool
    permissions: List[str]

class PermissionCreate(BaseModel):
    """Schema for permission creation."""
    name: str
    description: Optional[str] = None
    resource: str
    action: str

class PermissionInDB(BaseSchema):
    """Schema for permission in database."""
    name: str
    description: Optional[str]
    resource: str
    action: str

class TokenCreate(BaseModel):
    """Schema for token creation."""
    user_id: int
    token_type: str
    expires_at: datetime
    device_info: Optional[str] = None

class TokenInDB(BaseSchema):
    """Schema for token in database."""
    token: str
    token_type: str
    expires_at: datetime
    is_revoked: bool
    device_info: Optional[str]
