"""
Pydantic schemas for image processing.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ImageMetadata(BaseModel):
    """Image metadata schema."""
    
    hash: str = Field(..., description="SHA-256 hash of image content")
    company_id: int = Field(..., description="Company ID")
    original_filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="Content type (e.g., image/jpeg)")
    size: int = Field(..., description="File size in bytes")
    dimensions: tuple[int, int] = Field(
        ...,
        description="Image dimensions (width, height)"
    )
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    s3_key: str = Field(..., description="S3 object key")
    url: str = Field(..., description="CDN URL")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ImageResponse(BaseModel):
    """API response schema for image operations."""
    
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Response data"
    )
