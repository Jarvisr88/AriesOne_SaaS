"""
Common Database Models Module

This module provides SQLAlchemy models for common data persistence.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....database import Base
from ..common_models import ApplicationName, DataCenterType, LineOfBusiness

class ApplicationDB(Base):
    """Database model for application configuration."""
    __tablename__ = "applications"

    app_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[ApplicationName] = mapped_column(Enum(ApplicationName))
    facility_state: Mapped[str] = mapped_column(String(2))
    line_of_business: Mapped[LineOfBusiness] = mapped_column(Enum(LineOfBusiness))
    data_center: Mapped[DataCenterType] = mapped_column(Enum(DataCenterType))
    pptn_region: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    credentials = relationship("CredentialDB", back_populates="application")
    errors = relationship("ErrorDB", back_populates="application")

class CredentialDB(Base):
    """Database model for credentials."""
    __tablename__ = "credentials"

    credential_id: Mapped[UUID] = mapped_column(primary_key=True)
    app_id: Mapped[str] = mapped_column(ForeignKey("applications.app_id"))
    username: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(255))  # Encrypted
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    application = relationship("ApplicationDB", back_populates="credentials")

class ErrorDB(Base):
    """Database model for errors."""
    __tablename__ = "errors"

    error_id: Mapped[UUID] = mapped_column(primary_key=True)
    app_id: Mapped[str] = mapped_column(ForeignKey("applications.app_id"))
    source: Mapped[str] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(500))
    stack_trace: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    application = relationship("ApplicationDB", back_populates="errors")
    details = relationship("ErrorDetailDB", back_populates="error")

class ErrorDetailDB(Base):
    """Database model for error details."""
    __tablename__ = "error_details"

    detail_id: Mapped[UUID] = mapped_column(primary_key=True)
    error_id: Mapped[UUID] = mapped_column(ForeignKey("errors.error_id"))
    code: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(String(500))
    field: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(nullable=True)

    # Relationships
    error = relationship("ErrorDB", back_populates="details")
