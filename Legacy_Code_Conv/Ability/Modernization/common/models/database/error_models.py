"""
Error Database Models Module

This module provides SQLAlchemy models for error-related data.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class ErrorDB(Base):
    """Error database model."""

    __tablename__ = "errors"

    error_id: Mapped[UUID] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
