"""
Pydantic schemas for the imaging service.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    detail: str = Field(..., description="Error details")


class ImageMetadata(BaseModel):
    """Image metadata schema."""
    
    key: str = Field(..., description="S3 object key")
    size: int = Field(..., description="File size in bytes")
    etag: str = Field(..., description="S3 ETag")
    last_modified: datetime = Field(..., description="Last modified timestamp")
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Image metadata"
    )
    presigned_url: Optional[str] = Field(
        None,
        description="Presigned download URL"
    )
    cdn_url: str = Field(..., description="CloudFront URL")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ImageUploadResponse(BaseModel):
    """Image upload response schema."""
    
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Upload details")


class ImageListResponse(BaseModel):
    """Image list response schema."""
    
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: List[ImageMetadata] = Field(..., description="List of images")
