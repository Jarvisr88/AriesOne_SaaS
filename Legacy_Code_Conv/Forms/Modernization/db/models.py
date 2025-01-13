"""Database models for the Forms module.

This module defines SQLAlchemy models for form-related data.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

from core.db.base import Base
from auth.models import User


class Form(AsyncAttrs, Base):
    """Form model for storing form definitions."""
    
    __tablename__ = "forms"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    schema: Mapped[dict] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    creator: Mapped[User] = relationship(
        foreign_keys=[created_by]
    )
    submissions: Mapped[list["FormSubmission"]] = relationship(
        back_populates="form",
        cascade="all, delete-orphan"
    )
    company_forms: Mapped[list["CompanyForm"]] = relationship(
        back_populates="form",
        cascade="all, delete-orphan"
    )


class FormSubmission(AsyncAttrs, Base):
    """Form submission model for storing form responses."""
    
    __tablename__ = "form_submissions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    form_id: Mapped[int] = mapped_column(ForeignKey("forms.id"))
    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    data: Mapped[dict] = mapped_column(JSON)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    
    # Relationships
    form: Mapped[Form] = relationship(
        back_populates="submissions"
    )
    submitter: Mapped[User] = relationship(
        foreign_keys=[submitted_by]
    )
    company: Mapped["Company"] = relationship(
        back_populates="form_submissions"
    )


class Company(AsyncAttrs, Base):
    """Company model for multi-tenant support."""
    
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    form_submissions: Mapped[list[FormSubmission]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan"
    )
    company_forms: Mapped[list["CompanyForm"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan"
    )


class CompanyForm(AsyncAttrs, Base):
    """Association model for company-specific form configurations."""
    
    __tablename__ = "company_forms"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    form_id: Mapped[int] = mapped_column(ForeignKey("forms.id"))
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    company: Mapped[Company] = relationship(
        back_populates="company_forms"
    )
    form: Mapped[Form] = relationship(
        back_populates="company_forms"
    )
