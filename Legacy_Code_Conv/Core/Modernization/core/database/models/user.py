"""
Core User Model Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class User(Base):
    """User model for authentication and authorization."""
    
    # Authentication Fields
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Account Status
    email_verified: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        nullable=True
    )
    failed_login_attempts: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        nullable=True
    )
    
    # Multi-tenancy
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Security
    mfa_enabled: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )
    mfa_secret: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True
    )
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users", lazy="selectin")
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        lazy="selectin"
    )
    roles = relationship(
        "UserRole",
        back_populates="user",
        lazy="selectin"
    )
    sessions = relationship(
        "UserSession",
        back_populates="user",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<User {self.email}>"


class UserProfile(Base):
    """User profile information."""
    
    # User Reference
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    
    # Basic Information
    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Contact Information
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    postal_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Preferences
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default=text("'en'")
    )
    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'UTC'")
    )
    theme: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'light'")
    )
    notifications_enabled: Mapped[bool] = mapped_column(
        nullable=False,
        default=True
    )
    
    # Relationships
    user = relationship("User", back_populates="profile", lazy="selectin")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<UserProfile {self.first_name} {self.last_name}>"


class UserRole(Base):
    """User role assignments."""
    
    # References
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    # Role Details
    permissions: Mapped[list] = mapped_column(
        nullable=False,
        server_default=text("'[]'::jsonb")
    )
    scope: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'tenant'")
    )
    
    # Relationships
    user = relationship("User", back_populates="roles", lazy="selectin")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<UserRole {self.role_name}>"


class UserSession(Base):
    """User session tracking."""
    
    # References
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Session Information
    token: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        nullable=False
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 length
        nullable=True
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    device_info: Mapped[Optional[dict]] = mapped_column(
        nullable=True
    )
    
    # Session Status
    is_revoked: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True
    )
    revocation_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Relationships
    user = relationship("User", back_populates="sessions", lazy="selectin")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<UserSession {self.token[:8]}...>"
