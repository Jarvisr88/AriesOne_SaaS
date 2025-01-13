"""
File Models Module

This module provides file-related data models.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

class FileMetadata(BaseModel):
    """File metadata model."""

    file_id: UUID = Field(default_factory=uuid4)
    filename: str = Field(..., description="Storage filename")
    original_filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="File MIME type")
    size: int = Field(..., description="File size in bytes")
    user_id: UUID = Field(..., description="ID of user who uploaded file")
    metadata: dict = Field(default_factory=dict, description="Custom metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(None)

    @validator("size")
    def validate_size(cls, v: int) -> int:
        """Validate file size."""
        if v < 0:
            raise ValueError("File size cannot be negative")
        return v

    class Config:
        """Model configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True

class FileUploadResponse(BaseModel):
    """File upload response model."""

    file_id: UUID
    filename: str
    size: int
    content_type: str
    metadata: dict

class FileDownloadResponse(BaseModel):
    """File download response model."""

    file_id: UUID
    filename: str
    content_type: str
    size: int
    download_url: str
    expires_at: datetime
