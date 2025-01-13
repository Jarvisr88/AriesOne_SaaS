"""
Ability Database Models Module

This module provides SQLAlchemy models for Ability data persistence.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....database import Base

class CredentialsDB(Base):
    """Base database model for credentials."""
    __tablename__ = "credentials"
    __table_args__ = {"schema": "ability"}

    credential_id: Mapped[UUID] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))  # Discriminator
    sender_id: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(1000))  # Encrypted
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    __mapper_args__ = {
        "polymorphic_identity": "base",
        "polymorphic_on": type
    }

class EnvelopeCredentialsDB(CredentialsDB):
    """Database model for envelope credentials."""
    __tablename__ = "envelope_credentials"
    __table_args__ = {"schema": "ability"}

    credential_id: Mapped[UUID] = mapped_column(
        ForeignKey("ability.credentials.credential_id"),
        primary_key=True
    )
    envelope_id: Mapped[str] = mapped_column(String(100))
    environment: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {
        "polymorphic_identity": "envelope"
    }

class EligibilityCredentialsDB(CredentialsDB):
    """Database model for eligibility credentials."""
    __tablename__ = "eligibility_credentials"
    __table_args__ = {"schema": "ability"}

    credential_id: Mapped[UUID] = mapped_column(
        ForeignKey("ability.credentials.credential_id"),
        primary_key=True
    )
    facility_id: Mapped[str] = mapped_column(String(100))
    api_key: Mapped[str] = mapped_column(String(1000))  # Encrypted

    __mapper_args__ = {
        "polymorphic_identity": "eligibility"
    }

class ClerkCredentialsDB(CredentialsDB):
    """Database model for clerk credentials."""
    __tablename__ = "clerk_credentials"
    __table_args__ = {"schema": "ability"}

    credential_id: Mapped[UUID] = mapped_column(
        ForeignKey("ability.credentials.credential_id"),
        primary_key=True
    )
    clerk_id: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(50))
    permissions: Mapped[list[str]] = mapped_column(JSONB)

    __mapper_args__ = {
        "polymorphic_identity": "clerk"
    }

class IntegrationSettingsDB(Base):
    """Database model for integration settings."""
    __tablename__ = "integration_settings"
    __table_args__ = {"schema": "ability"}

    settings_id: Mapped[UUID] = mapped_column(primary_key=True)
    credentials_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("ability.credentials.credential_id"),
        nullable=True
    )
    clerk_credentials_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("ability.clerk_credentials.credential_id"),
        nullable=True
    )
    eligibility_credentials_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("ability.eligibility_credentials.credential_id"),
        nullable=True
    )
    envelope_credentials_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("ability.envelope_credentials.credential_id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    credentials = relationship("CredentialsDB", foreign_keys=[credentials_id])
    clerk_credentials = relationship("ClerkCredentialsDB", foreign_keys=[clerk_credentials_id])
    eligibility_credentials = relationship("EligibilityCredentialsDB", foreign_keys=[eligibility_credentials_id])
    envelope_credentials = relationship("EnvelopeCredentialsDB", foreign_keys=[envelope_credentials_id])
