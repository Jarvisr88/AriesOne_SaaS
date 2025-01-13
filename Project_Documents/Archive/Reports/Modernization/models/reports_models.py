"""Reports models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean,
    Table,
    Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, Field, validator
import re

from ...Core.Modernization.models.base import Base


class ReportType(str, Enum):
    """Report type."""
    CUSTOM = "custom"
    SYSTEM = "system"
    TEMPLATE = "template"


class ReportFormat(str, Enum):
    """Report format."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"


class Report(Base):
    """Report model."""
    __tablename__ = "reports"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    file_name: Mapped[str] = mapped_column(String(200))
    type: Mapped[ReportType] = mapped_column(String(20))
    is_system: Mapped[bool] = mapped_column(default=False)
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("report_templates.id"),
        nullable=True
    )
    parameters: Mapped[Optional[Dict]] = mapped_column(JSONB)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(default=1)
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="reports")
    history = relationship(
        "ReportHistory",
        back_populates="report",
        order_by="desc(ReportHistory.created_at)"
    )


class ReportTemplate(Base):
    """Report template model."""
    __tablename__ = "report_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    file_name: Mapped[str] = mapped_column(String(200))
    is_system: Mapped[bool] = mapped_column(default=False)
    parameters: Mapped[Optional[Dict]] = mapped_column(JSONB)
    content: Mapped[str] = mapped_column(Text)
    format: Mapped[ReportFormat] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(default=1)
    
    # Relationships
    reports = relationship("Report", back_populates="template")
    history = relationship(
        "ReportTemplateHistory",
        back_populates="template",
        order_by="desc(ReportTemplateHistory.created_at)"
    )


class ReportHistory(Base):
    """Report history model."""
    __tablename__ = "report_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    file_name: Mapped[str] = mapped_column(String(200))
    type: Mapped[ReportType] = mapped_column(String(20))
    is_system: Mapped[bool] = mapped_column(default=False)
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("report_templates.id"),
        nullable=True
    )
    parameters: Mapped[Optional[Dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Relationships
    report = relationship("Report", back_populates="history")


class ReportTemplateHistory(Base):
    """Report template history model."""
    __tablename__ = "report_template_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("report_templates.id")
    )
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    file_name: Mapped[str] = mapped_column(String(200))
    is_system: Mapped[bool] = mapped_column(default=False)
    parameters: Mapped[Optional[Dict]] = mapped_column(JSONB)
    content: Mapped[str] = mapped_column(Text)
    format: Mapped[ReportFormat] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="history")


# Pydantic models for API
class ReportBase(BaseModel):
    """Base report model."""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    file_name: str = Field(..., min_length=1, max_length=200)
    type: ReportType
    is_system: bool = False
    template_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Validate report name."""
        if not re.match(r'^[A-Za-z0-9_\- ]+$', v):
            raise ValueError("Invalid report name")
        return v
    
    @validator('file_name')
    def validate_file_name(cls, v):
        """Validate file name."""
        if not re.match(r'^[A-Za-z0-9_\-\.]+$', v):
            raise ValueError("Invalid file name")
        return v
    
    @validator('parameters')
    def validate_parameters(cls, v):
        """Validate parameters."""
        if v:
            for key in v.keys():
                if not re.match(r'^[A-Za-z0-9_]+$', key):
                    raise ValueError(f"Invalid parameter name: {key}")
        return v


class ReportCreate(ReportBase):
    """Report create model."""
    pass


class ReportUpdate(BaseModel):
    """Report update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    parameters: Optional[Dict[str, Any]] = None
    reason: Optional[str] = Field(None, max_length=200)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate report name."""
        if v and not re.match(r'^[A-Za-z0-9_\- ]+$', v):
            raise ValueError("Invalid report name")
        return v


class ReportResponse(ReportBase):
    """Report response model."""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    version: int
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class ReportTemplateBase(BaseModel):
    """Base report template model."""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    file_name: str = Field(..., min_length=1, max_length=200)
    is_system: bool = False
    parameters: Optional[Dict[str, Any]] = None
    content: str
    format: ReportFormat
    
    @validator('name')
    def validate_name(cls, v):
        """Validate template name."""
        if not re.match(r'^[A-Za-z0-9_\- ]+$', v):
            raise ValueError("Invalid template name")
        return v
    
    @validator('file_name')
    def validate_file_name(cls, v):
        """Validate file name."""
        if not re.match(r'^[A-Za-z0-9_\-\.]+$', v):
            raise ValueError("Invalid file name")
        return v


class ReportTemplateCreate(ReportTemplateBase):
    """Report template create model."""
    pass


class ReportTemplateUpdate(BaseModel):
    """Report template update model."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    parameters: Optional[Dict[str, Any]] = None
    content: Optional[str] = None
    format: Optional[ReportFormat] = None
    reason: Optional[str] = Field(None, max_length=200)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate template name."""
        if v and not re.match(r'^[A-Za-z0-9_\- ]+$', v):
            raise ValueError("Invalid template name")
        return v


class ReportTemplateResponse(ReportTemplateBase):
    """Report template response model."""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    version: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class ReportHistoryResponse(BaseModel):
    """Report history response model."""
    id: int
    name: str
    category: str
    file_name: str
    type: ReportType
    is_system: bool
    template_id: Optional[int]
    parameters: Optional[Dict[str, Any]]
    created_at: datetime
    created_by: int
    reason: Optional[str]
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class ReportTemplateHistoryResponse(BaseModel):
    """Report template history response model."""
    id: int
    name: str
    category: str
    file_name: str
    is_system: bool
    parameters: Optional[Dict[str, Any]]
    content: str
    format: ReportFormat
    created_at: datetime
    created_by: int
    reason: Optional[str]
    
    class Config:
        """Pydantic config."""
        orm_mode = True
