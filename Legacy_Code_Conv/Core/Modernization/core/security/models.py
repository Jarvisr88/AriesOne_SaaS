"""
Core Security Models Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides security-related database models.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import String, Table, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Role(Base):
    """Role model for RBAC."""
    
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    permissions: Mapped[List["Permission"]] = relationship(
        secondary="role_permissions",
        back_populates="roles"
    )
    users: Mapped[List["User"]] = relationship(
        secondary="user_roles",
        back_populates="roles"
    )


class Permission(Base):
    """Permission model for RBAC."""
    
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    roles: Mapped[List[Role]] = relationship(
        secondary="role_permissions",
        back_populates="permissions"
    )


# Association tables
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    mapped_column("role_id", ForeignKey("role.id"), primary_key=True),
    mapped_column("permission_id", ForeignKey("permission.id"), primary_key=True)
)

user_roles = Table(
    "user_roles",
    Base.metadata,
    mapped_column("user_id", ForeignKey("user.id"), primary_key=True),
    mapped_column("role_id", ForeignKey("role.id"), primary_key=True)
)


class User(Base):
    """User model with security features."""
    
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    roles: Mapped[List[Role]] = relationship(
        secondary=user_roles,
        back_populates="users"
    )


class SecurityAuditLog(Base):
    """Security audit log model."""
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("user.id"))
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(String(500))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )


class AccessToken(Base):
    """Access token model for OAuth2."""
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(500), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(default=False)
    scope: Mapped[Optional[str]] = mapped_column(String(200))


class RefreshToken(Base):
    """Refresh token model for OAuth2."""
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(500), nullable=False)
    access_token_id: Mapped[UUID] = mapped_column(
        ForeignKey("accesstoken.id"),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(default=False)
