"""Base model module.

This module provides the base SQLAlchemy model with common fields
and functionality for all database models.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    declared_attr
)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models."""
    
    # Make tablename lowercase class name
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Get table name from class name."""
        return cls.__name__.lower()


class TimestampMixin:
    """Mixin to add timestamp fields."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class SoftDeleteMixin:
    """Mixin to add soft delete functionality."""
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


class UUIDMixin:
    """Mixin to add UUID primary key."""
    
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
