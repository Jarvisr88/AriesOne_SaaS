"""Base model for all database entities."""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from uuid import UUID, uuid4


class Base(DeclarativeBase):
    """Base class for all database models."""

    @declared_attr
    def __tablename__(cls) -> str:
        """Get table name from class name."""
        return cls.__name__.lower()

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Base":
        """Create model instance from dictionary."""
        return cls(**data)

    def update(self, data: Dict[str, Any]) -> None:
        """Update model attributes from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
