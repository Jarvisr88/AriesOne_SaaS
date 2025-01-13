"""Organization models for AriesOne SaaS platform."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, DateTime, JSON, ForeignKey, Enum as SQLAEnum, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from uuid import UUID

from .base import Base

class OrganizationType(enum.Enum):
    """Organization type enumeration."""
    PROVIDER = "provider"
    SUPPLIER = "supplier"
    PARTNER = "partner"
    CLIENT = "client"

class OrganizationStatus(enum.Enum):
    """Organization status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class Organization(Base):
    """Organization model for managing healthcare providers and suppliers."""

    __tablename__ = "organizations"

    # Basic information
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    type: Mapped[OrganizationType] = mapped_column(SQLAEnum(OrganizationType))
    status: Mapped[OrganizationStatus] = mapped_column(
        SQLAEnum(OrganizationStatus),
        default=OrganizationStatus.PENDING
    )
    
    # Contact information
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    fax: Mapped[Optional[str]] = mapped_column(String(20))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Address information
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    country: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Business information
    tax_id: Mapped[Optional[str]] = mapped_column(String(50))
    npi: Mapped[Optional[str]] = mapped_column(String(20))
    medicare_id: Mapped[Optional[str]] = mapped_column(String(20))
    medicaid_id: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Additional information
    settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Relationships
    users: Mapped[List["UserOrganization"]] = relationship(
        "UserOrganization",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL")
    )
    children: Mapped[List["Organization"]] = relationship(
        "Organization",
        backref=relationship.backref("parent", remote_side="Organization.id"),
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert organization to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "type": self.type.value,
            "status": self.status.value,
            "email": self.email,
            "phone": self.phone,
            "fax": self.fax,
            "website": self.website,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "tax_id": self.tax_id,
            "npi": self.npi,
            "medicare_id": self.medicare_id,
            "medicaid_id": self.medicaid_id,
            "settings": self.settings,
            "metadata": self.metadata,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class UserOrganization(Base):
    """Association model for user-organization relationships."""

    __tablename__ = "user_organizations"

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Role information
    role: Mapped[str] = mapped_column(String(50))
    permissions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Metadata
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="organizations")
    organization: Mapped[Organization] = relationship(
        Organization,
        back_populates="users"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert user organization to dictionary."""
        return {
            "user_id": str(self.user_id),
            "organization_id": str(self.organization_id),
            "role": self.role,
            "permissions": self.permissions,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
