"""SODA resource models module."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class HumanAddress(BaseModel):
    """Model for human-readable addresses."""
    
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

class Location(BaseModel):
    """Model for location data."""
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    human_address: Optional[HumanAddress] = None

class Phone(BaseModel):
    """Model for phone numbers."""
    
    phone_number: str
    phone_type: str = Field(..., regex='^(fax|voice|tty|cell)$')
    area_code: Optional[str] = None
    extension: Optional[str] = None

class WebsiteUrl(BaseModel):
    """Model for website URLs."""
    
    url: HttpUrl
    description: Optional[str] = None

class ResourceColumn(BaseModel):
    """Model for resource columns."""
    
    name: str
    field_name: str
    datatype: str
    description: Optional[str] = None
    position: int
    is_primary: bool = False

class ResourceMetadata(BaseModel):
    """Model for resource metadata."""
    
    id: str = Field(..., regex='^[a-z0-9]{4}-[a-z0-9]{4}$')
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    attribution: Optional[str] = None
    attribution_link: Optional[HttpUrl] = None
    contact_email: Optional[str] = None
    type: str
    updatedAt: datetime
    createdAt: datetime
    metadata_updated_at: datetime
    data_updated_at: datetime
    license: Optional[str] = None
    columns: List[ResourceColumn]
    row_count: int = 0
    download_count: int = 0
    custom_fields: Optional[Dict[str, Any]] = None

class SodaResult(BaseModel):
    """Model for SODA API results."""
    
    by: Optional[str] = None
    record_count: int = 0
    error: bool = False
    error_message: Optional[str] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    deleted: Optional[int] = None
