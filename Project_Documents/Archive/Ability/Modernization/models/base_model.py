from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

# Convention for constraint naming
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)

class Base(DeclarativeBase):
    """Base class for all models in the application."""
    
    metadata = metadata
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name automatically from class name."""
        return cls.__name__.lower()
    
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Base":
        """Create model instance from dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__table__.columns
        })
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
