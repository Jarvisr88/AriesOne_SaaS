"""
Models for the Imaging module.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import magic
import mimetypes

class ImageType(str, Enum):
    """Image type enumeration."""
    JPEG = "image/jpeg"
    PNG = "image/png"
    TIFF = "image/tiff"
    PDF = "application/pdf"
    DICOM = "application/dicom"

class ImageMetadata(BaseModel):
    """Image metadata model."""
    filename: str
    mime_type: str
    size_bytes: int
    width: Optional[int] = None
    height: Optional[int] = None
    dpi: Optional[int] = None
    color_space: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    company_id: str
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

    @validator('mime_type')
    def validate_mime_type(cls, v):
        """Validate mime type."""
        if v not in [t.value for t in ImageType]:
            raise ValueError(f"Unsupported mime type: {v}")
        return v

class ImageProcessingOptions(BaseModel):
    """Image processing options."""
    resize: Optional[Dict[str, int]] = None  # width, height
    format: Optional[ImageType] = None
    quality: Optional[int] = Field(None, ge=1, le=100)
    optimize: bool = True
    preserve_metadata: bool = True

class ProcessedImage(BaseModel):
    """Processed image result."""
    original_metadata: ImageMetadata
    processed_metadata: ImageMetadata
    processing_time: float
    options_used: ImageProcessingOptions

class ImageUploadResult(BaseModel):
    """Image upload result."""
    metadata: ImageMetadata
    url: str
    thumbnail_url: Optional[str] = None
    processing_result: Optional[ProcessedImage] = None

class ImageBatch(BaseModel):
    """Batch of images for processing."""
    images: List[str]  # List of image IDs
    options: ImageProcessingOptions
    callback_url: Optional[str] = None

class StorageLocation(str, Enum):
    """Storage location enumeration."""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"

class StorageConfig(BaseModel):
    """Storage configuration."""
    location: StorageLocation
    bucket: Optional[str] = None
    prefix: Optional[str] = None
    endpoint: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
    
    class Config:
        """Pydantic config."""
        extra = "allow"

class ImageSearchQuery(BaseModel):
    """Image search query."""
    company_id: str
    mime_types: Optional[List[ImageType]] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    filename_pattern: Optional[str] = None
    metadata_query: Optional[Dict[str, Any]] = None
    page: int = 1
    page_size: int = 50

class ImageSearchResult(BaseModel):
    """Image search result."""
    total: int
    page: int
    page_size: int
    results: List[ImageMetadata]
