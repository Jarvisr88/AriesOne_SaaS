"""
Error Models Module

This module provides error-related data models.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

class Error(BaseModel):
    """Error model."""

    error_id: UUID = Field(default_factory=uuid4)
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    stack_trace: Optional[str] = Field(None, description="Error stack trace")
    user_id: Optional[UUID] = Field(None, description="ID of affected user")
    request_id: Optional[str] = Field(None, description="Request ID")
    severity: str = Field(..., description="Error severity")
    source: str = Field(..., description="Error source")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Model configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True

class ErrorResponse(BaseModel):
    """Error response model."""

    error_id: UUID
    code: str
    message: str
    details: Optional[dict] = None
    request_id: Optional[str] = None
