"""Authentication models module.

This module defines SQLAlchemy models for user authentication and authorization.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

from core.db.base import Base


class User(AsyncAttrs, Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        lazy="selectin"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
        lazy="selectin"
    )


class Role(AsyncAttrs, Base):
    """Role model for authorization."""
    
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    users: Mapped[list[User]] = relationship(
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin"
    )


class Permission(AsyncAttrs, Base):
    """Permission model for fine-grained access control."""
    
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    roles: Mapped[list[Role]] = relationship(
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin"
    )


class AuditLog(AsyncAttrs, Base):
    """Audit log for tracking authentication and authorization events."""
    
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(50))
    details: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )  # IPv6 length
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    
    # Relationships
    user: Mapped[User] = relationship(back_populates="audit_logs")


# Association tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True)
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True)
)
