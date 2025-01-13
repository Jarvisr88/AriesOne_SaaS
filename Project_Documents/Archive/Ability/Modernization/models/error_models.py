"""Error tracking models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as SQLUUID

from ....Core.Modernization.models.base import Base


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorLog(Base):
    """Error log model."""
    __tablename__ = "error_logs"
    
    id = Column(
        SQLUUID(as_uuid=True),
        primary_key=True
    )
    error_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    severity = Column(
        SQLEnum(ErrorSeverity),
        nullable=False,
        default=ErrorSeverity.ERROR
    )
    request_data = Column(JSONB, nullable=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=True
    )
    metadata = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )


class ErrorLogBase(BaseModel):
    """Base error log model."""
    error_type: str
    message: str
    stack_trace: Optional[str] = None
    severity: ErrorSeverity = ErrorSeverity.ERROR
    request_data: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ErrorLogCreate(ErrorLogBase):
    """Error log create model."""
    pass


class ErrorLogResponse(ErrorLogBase):
    """Error log response model."""
    id: UUID
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class ErrorLogFilter(BaseModel):
    """Error log filter model."""
    error_type: Optional[str] = None
    severity: Optional[ErrorSeverity] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ErrorStats(BaseModel):
    """Error statistics model."""
    total_errors: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
