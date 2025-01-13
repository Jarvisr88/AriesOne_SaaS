"""Report schemas module."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ReportBase(BaseModel):
    """Base schema for reports."""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    """Schema for creating a report."""
    file_name: str = Field(..., min_length=1, max_length=255)
    is_system: Optional[bool] = False

class ReportUpdate(BaseModel):
    """Schema for updating a report."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_system: Optional[bool] = None

class ReportInDB(ReportBase):
    """Schema for report in database."""
    id: int
    file_name: str
    is_system: bool
    is_deleted: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True

class ReportExecutionBase(BaseModel):
    """Base schema for report executions."""
    parameters: Optional[Dict[str, Any]] = None

class ReportExecutionCreate(ReportExecutionBase):
    """Schema for creating a report execution."""
    pass

class ReportExecutionInDB(ReportExecutionBase):
    """Schema for report execution in database."""
    id: int
    report_id: int
    user_id: int
    status: str
    result_file: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True

class ReportTemplateBase(BaseModel):
    """Base schema for report templates."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    template_type: str = Field(..., regex='^(sql|jinja|custom)$')
    content: str
    parameters: Optional[Dict[str, Any]] = None

class ReportTemplateCreate(ReportTemplateBase):
    """Schema for creating a report template."""
    pass

class ReportTemplateUpdate(BaseModel):
    """Schema for updating a report template."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    content: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class ReportTemplateInDB(ReportTemplateBase):
    """Schema for report template in database."""
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True
