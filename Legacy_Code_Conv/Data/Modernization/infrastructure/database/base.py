"""SQLAlchemy base configuration."""
from typing import Any
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func

class Base(DeclarativeBase):
    """Base class for all database models."""

    @declared_attr
    def __tablename__(cls) -> str:
        """Get table name from class name."""
        return f"tbl_{cls.__name__.lower()}"

class TimestampMixin:
    """Mixin for created and updated timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
