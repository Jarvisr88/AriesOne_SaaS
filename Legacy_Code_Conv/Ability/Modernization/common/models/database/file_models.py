"""
File Database Models Module

This module provides SQLAlchemy models for file-related data.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class FileMetadataDB(Base):
    """File metadata database model."""

    __tablename__ = "file_metadata"

    file_id: Mapped[UUID] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
