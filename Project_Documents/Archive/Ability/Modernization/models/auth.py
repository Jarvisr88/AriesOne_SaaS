"""Authentication models module."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import bcrypt

Base = declarative_base()

# Many-to-many relationship table for users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    """User model for authentication."""
    
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(32))
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")

    def set_password(self, password: str) -> None:
        """Hash and set user password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str) -> bool:
        """Verify user password."""
        return bcrypt.checkpw(
            password.encode(),
            self.password_hash.encode()
        )

class Role(Base):
    """Role model for RBAC."""
    
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", back_populates="role")

class Permission(Base):
    """Permission model for RBAC."""
    
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)  # create, read, update, delete
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="permissions")

class RefreshToken(Base):
    """Refresh token model for OAuth2."""
    
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

# Pydantic models for API requests/responses
class TokenRequest(BaseModel):
    """Token request model."""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []

class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_mfa_enabled: bool
    roles: List[str]
    created_at: datetime
    updated_at: datetime

class MFASetup(BaseModel):
    """MFA setup response model."""
    secret: str
    qr_code: str
    backup_codes: List[str]
