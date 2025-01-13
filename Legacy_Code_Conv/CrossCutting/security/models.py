"""Security models module."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from app.database import Base

# Many-to-many association table for user roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    """User model."""
    
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    access_tokens = relationship("AccessToken", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Role(Base):
    """Role model."""
    
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    permissions = Column(String)  # JSON string of permissions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")

class AccessToken(Base):
    """Access token model."""
    
    __tablename__ = 'access_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="access_tokens")

class AuditLog(Base):
    """Audit log model."""
    
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(String)
    details = Column(String)  # JSON string of additional details
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

# Pydantic models for API
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    """User creation schema."""
    password: str

class UserUpdate(UserBase):
    """User update schema."""
    password: Optional[str] = None

class UserInDB(UserBase):
    """User database schema."""
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True

class RoleBase(BaseModel):
    """Base role schema."""
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = []

class RoleCreate(RoleBase):
    """Role creation schema."""
    pass

class RoleUpdate(RoleBase):
    """Role update schema."""
    pass

class RoleInDB(RoleBase):
    """Role database schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True

class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token data schema."""
    email: Optional[str] = None
