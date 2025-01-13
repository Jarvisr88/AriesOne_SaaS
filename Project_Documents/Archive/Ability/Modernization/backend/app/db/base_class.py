from typing import Any
from datetime import datetime
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime
import uuid

@as_declarative()
class Base:
    """Base class for all database models"""
    
    id: Any
    created_at: datetime
    updated_at: datetime
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Default columns for all tables
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
