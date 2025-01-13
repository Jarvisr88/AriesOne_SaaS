"""Session model module."""
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, Enum, Numeric
import enum

from infrastructure.database.base import Base, TimestampMixin

class SessionStatus(str, enum.Enum):
    """Session status enumeration."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    VOID = "void"
    REFUNDED = "refunded"

class Session(Base, TimestampMixin):
    """Session model representing patient appointments."""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("tbl_company.id"), nullable=False)
    location_id: Mapped[UUID] = mapped_column(ForeignKey("tbl_location.id"), nullable=False)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("tbl_patient.id"), nullable=False)
    provider_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("tbl_provider.id"))
    
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), 
        default=SessionStatus.SCHEDULED,
        nullable=False
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )
    
    amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    notes: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Relationships
    company = relationship("Company", back_populates="sessions")
    location = relationship("Location", back_populates="sessions")
    patient = relationship("Patient", back_populates="sessions")
    provider = relationship("Provider", back_populates="sessions")
    payments = relationship("Payment", back_populates="session")
    
    def __repr__(self) -> str:
        """String representation of Session."""
        return (
            f"Session(id={self.id}, patient_id={self.patient_id}, "
            f"scheduled_start={self.scheduled_start}, status={self.status})"
        )
