"""User model for AriesOne SaaS platform."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, DateTime, JSON, Boolean, Enum as SQLAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from uuid import UUID

from .base import Base

class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    USER = "user"

class UserStatus(enum.Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    # Basic information
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    # Personal information
    first_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[Optional[str]] = mapped_column(String(50))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Status and role
    role: Mapped[UserRole] = mapped_column(
        SQLAEnum(UserRole),
        default=UserRole.USER
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLAEnum(UserStatus),
        default=UserStatus.PENDING
    )
    
    # Account settings
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Timestamps
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    sessions: Mapped[List["Session"]] = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    organizations: Mapped[List["UserOrganization"]] = relationship(
        "UserOrganization",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @hybrid_property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary."""
        data = {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "role": self.role.value,
            "status": self.status.value,
            "is_verified": self.is_verified,
            "is_2fa_enabled": self.is_2fa_enabled,
            "preferences": self.preferences,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data["password_hash"] = self.password_hash
            
        return data

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()

    def verify_email(self) -> None:
        """Mark email as verified."""
        self.is_verified = True
        self.email_verified_at = datetime.utcnow()
        self.status = UserStatus.ACTIVE
