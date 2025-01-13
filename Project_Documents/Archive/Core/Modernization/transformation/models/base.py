"""
Base models for the Core module.
Provides foundational database models and Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel as PydanticBaseModel, Field

Base = declarative_base()

class BaseDBModel(Base):
    """Base SQLAlchemy model with common fields."""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(50))
    updated_by = Column(String(50))
    is_active = Column(Boolean, default=True, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

class BaseSchema(PydanticBaseModel):
    """Base Pydantic model with common fields."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_active: bool = True

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class AuditLog(BaseDBModel):
    """Audit log for tracking changes."""
    __tablename__ = "core_audit_log"

    entity_name = Column(String(100), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)
    changes = Column(String, nullable=True)
    user_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class AuditLogSchema(BaseSchema):
    """Pydantic schema for audit log."""
    entity_name: str
    entity_id: int
    action: str
    changes: Optional[str]
    user_id: str
    timestamp: datetime

class ErrorLog(BaseDBModel):
    """Error logging model."""
    __tablename__ = "core_error_log"

    error_type = Column(String(100), nullable=False, index=True)
    error_message = Column(String, nullable=False)
    stack_trace = Column(String, nullable=True)
    context = Column(String, nullable=True)
    user_id = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class ErrorLogSchema(BaseSchema):
    """Pydantic schema for error log."""
    error_type: str
    error_message: str
    stack_trace: Optional[str]
    context: Optional[str]
    user_id: Optional[str]
    timestamp: datetime

class SystemConfig(BaseDBModel):
    """System configuration model."""
    __tablename__ = "core_system_config"

    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String(50), nullable=False, index=True)

class SystemConfigSchema(BaseSchema):
    """Pydantic schema for system configuration."""
    key: str
    value: str
    description: Optional[str]
    category: str
