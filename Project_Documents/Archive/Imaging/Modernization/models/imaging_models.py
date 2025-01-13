"""Models for image handling and MIME type configuration."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, validator
import re


class MimeType(BaseModel):
    """MIME type configuration."""
    
    id: str = Field(..., description="Unique identifier")
    extension: str = Field(..., description="File extension")
    mime_type: str = Field(..., description="MIME type")
    description: Optional[str] = Field(None, description="Description")
    
    @validator('extension')
    def validate_extension(cls, v):
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError('Extension must be alphanumeric')
        return v.lower()
    
    @validator('mime_type')
    def validate_mime_type(cls, v):
        if not re.match(r'^[a-zA-Z0-9-]+/[a-zA-Z0-9-+.]+$', v):
            raise ValueError('Invalid MIME type format')
        return v.lower()


class MimeTypeCreate(BaseModel):
    """Schema for creating MIME type."""
    
    extension: str = Field(..., description="File extension")
    mime_type: str = Field(..., description="MIME type")
    description: Optional[str] = Field(None, description="Description")


class ImageMetadata(BaseModel):
    """Image metadata."""
    
    id: str = Field(..., description="Unique identifier")
    company: str = Field(..., description="Company identifier")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="Content type")
    size: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp")
    
    @validator('filename')
    def validate_filename(cls, v):
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('Invalid filename')
        return v


class ImageResponse(BaseModel):
    """Response for image operations."""
    
    id: str = Field(..., description="Image identifier")
    url: HttpUrl = Field(..., description="Access URL")
    metadata: Optional[ImageMetadata] = Field(None, description="Image metadata")


class ImageUploadRequest(BaseModel):
    """Request for image upload."""
    
    company: str = Field(..., description="Company identifier")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="Content type")
    size: int = Field(..., description="File size in bytes")


class ImageListResponse(BaseModel):
    """Response for listing images."""
    
    images: List[ImageMetadata] = Field(..., description="List of images")
    total: int = Field(..., description="Total number of images")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Page size")


class ImageError(BaseModel):
    """Error response for image operations."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional details")
