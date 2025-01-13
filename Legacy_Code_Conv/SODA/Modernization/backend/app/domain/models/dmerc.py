"""DMERC models for AriesOne SaaS platform."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, DateTime, JSON, ForeignKey, Enum as SQLAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from uuid import UUID

from .base import Base
from .organization import Organization
from .user import User

class DMERCFormType(enum.Enum):
    """DMERC form type enumeration."""
    CMN = "cmn"
    DIF = "dif"
    AUTHORIZATION = "authorization"
    PRESCRIPTION = "prescription"
    ORDER = "order"

class DMERCStatus(enum.Enum):
    """DMERC status enumeration."""
    DRAFT = "draft"
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class DMERCForm(Base):
    """DMERC form model for managing medical equipment requests."""

    __tablename__ = "dmerc_forms"

    # Form information
    form_type: Mapped[DMERCFormType] = mapped_column(SQLAEnum(DMERCFormType))
    form_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    status: Mapped[DMERCStatus] = mapped_column(
        SQLAEnum(DMERCStatus),
        default=DMERCStatus.DRAFT
    )
    
    # Relationships
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
    organization: Mapped[Organization] = relationship("Organization")
    
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_by: Mapped[User] = relationship(
        "User",
        foreign_keys=[created_by_id]
    )
    
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[Optional[User]] = relationship(
        "User",
        foreign_keys=[updated_by_id]
    )
    
    # Patient information
    patient_id: Mapped[str] = mapped_column(String(50), index=True)
    patient_data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    
    # Form data
    form_data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    denied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Attachments
    attachments: Mapped[List["DMERCAttachment"]] = relationship(
        "DMERCAttachment",
        back_populates="form",
        cascade="all, delete-orphan"
    )
    
    # History
    history: Mapped[List["DMERCHistory"]] = relationship(
        "DMERCHistory",
        back_populates="form",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert DMERC form to dictionary."""
        return {
            "id": str(self.id),
            "form_type": self.form_type.value,
            "form_number": self.form_number,
            "status": self.status.value,
            "organization_id": str(self.organization_id),
            "created_by_id": str(self.created_by_id),
            "updated_by_id": str(self.updated_by_id) if self.updated_by_id else None,
            "patient_id": self.patient_id,
            "patient_data": self.patient_data,
            "form_data": self.form_data,
            "notes": self.notes,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "denied_at": self.denied_at.isoformat() if self.denied_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class DMERCAttachment(Base):
    """DMERC attachment model for managing form attachments."""

    __tablename__ = "dmerc_attachments"

    form_id: Mapped[UUID] = mapped_column(ForeignKey("dmerc_forms.id"))
    form: Mapped[DMERCForm] = relationship("DMERCForm", back_populates="attachments")
    
    file_name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(50))
    file_size: Mapped[int] = mapped_column()
    file_path: Mapped[str] = mapped_column(String(512))
    
    uploaded_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    uploaded_by: Mapped[User] = relationship("User")
    
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    def to_dict(self) -> Dict[str, Any]:
        """Convert attachment to dictionary."""
        return {
            "id": str(self.id),
            "form_id": str(self.form_id),
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "file_path": self.file_path,
            "uploaded_by_id": str(self.uploaded_by_id),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class DMERCHistory(Base):
    """DMERC history model for tracking form changes."""

    __tablename__ = "dmerc_history"

    form_id: Mapped[UUID] = mapped_column(ForeignKey("dmerc_forms.id"))
    form: Mapped[DMERCForm] = relationship("DMERCForm", back_populates="history")
    
    action: Mapped[str] = mapped_column(String(50))
    changes: Mapped[Dict[str, Any]] = mapped_column(JSON)
    
    performed_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    performed_by: Mapped[User] = relationship("User")
    
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    def to_dict(self) -> Dict[str, Any]:
        """Convert history entry to dictionary."""
        return {
            "id": str(self.id),
            "form_id": str(self.form_id),
            "action": self.action,
            "changes": self.changes,
            "performed_by_id": str(self.performed_by_id),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
