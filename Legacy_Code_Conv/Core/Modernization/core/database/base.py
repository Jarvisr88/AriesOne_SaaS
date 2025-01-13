"""
Core Database Base Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides the base SQLAlchemy model and metadata.
"""
import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Metadata with naming convention
metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    metadata = metadata
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()
    
    # Common columns for all tables
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    updated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    version: Mapped[int] = mapped_column(
        default=1,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update model from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.version += 1
