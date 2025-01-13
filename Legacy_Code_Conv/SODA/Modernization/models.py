"""
Models for the SODA (Socrata Open Data API) module.
"""
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator
import re

class SodaDataFormat(str, Enum):
    """SODA data format enumeration."""
    JSON = "json"
    CSV = "csv"
    XML = "xml"

class SoqlOrderDirection(str, Enum):
    """SOQL order direction enumeration."""
    ASC = "ASC"
    DESC = "DESC"

class HumanAddress(BaseModel):
    """Human-readable address model."""
    address: str
    city: str
    state: str
    zip: str
    country: Optional[str] = "USA"

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "address": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94105"
            }
        }

class Location(BaseModel):
    """Location model with coordinates."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[HumanAddress] = None
    needs_recoding: bool = False

class PhoneNumber(BaseModel):
    """Phone number model."""
    number: str
    type: Optional[str] = None
    country_code: str = "1"

    @validator('number')
    def validate_phone(cls, v):
        """Validate phone number format."""
        pattern = r'^\+?1?\d{10}$'
        if not re.match(pattern, re.sub(r'[\s\-\(\)]', '', v)):
            raise ValueError('Invalid phone number format')
        return v

class WebsiteUrl(BaseModel):
    """Website URL model."""
    url: HttpUrl
    description: Optional[str] = None
    last_checked: Optional[datetime] = None
    is_active: bool = True

class ResourceColumn(BaseModel):
    """Resource column metadata."""
    name: str
    field_name: str
    datatype: str
    description: Optional[str] = None
    is_primary: bool = False
    is_hidden: bool = False
    cacheable: bool = True

class ResourceMetadata(BaseModel):
    """Resource metadata."""
    id: str
    name: str
    description: Optional[str] = None
    domain: str
    created_at: datetime
    updated_at: datetime
    columns: List[ResourceColumn]
    row_count: int
    view_count: int
    category: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

    @validator('id')
    def validate_four_by_four(cls, v):
        """Validate Socrata four-by-four ID format."""
        if not re.match(r'^[a-z0-9]{4}-[a-z0-9]{4}$', v):
            raise ValueError('Invalid Socrata ID format')
        return v

class SoqlQuery(BaseModel):
    """SOQL query parameters."""
    select: List[str] = ["*"]
    where: Optional[str] = None
    order: Optional[List[str]] = None
    group: Optional[List[str]] = None
    limit: Optional[int] = Field(None, ge=0)
    offset: Optional[int] = Field(None, ge=0)
    q: Optional[str] = None

    def to_query_string(self) -> str:
        """Convert query parameters to SOQL query string."""
        parts = []
        
        if self.select != ["*"]:
            parts.append(f"$select={','.join(self.select)}")
        
        if self.where:
            parts.append(f"$where={self.where}")
        
        if self.order:
            parts.append(f"$order={','.join(self.order)}")
        
        if self.group:
            parts.append(f"$group={','.join(self.group)}")
        
        if self.limit is not None:
            parts.append(f"$limit={self.limit}")
        
        if self.offset is not None:
            parts.append(f"$offset={self.offset}")
        
        if self.q:
            parts.append(f"$q={self.q}")
        
        return "&".join(parts)

class SodaError(BaseModel):
    """SODA error response."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

class SodaResponse(BaseModel):
    """SODA API response."""
    data: List[Dict[str, Any]]
    metadata: Optional[ResourceMetadata] = None
    error: Optional[SodaError] = None
    total_count: Optional[int] = None
    cached: bool = False
    request_time: float = 0.0

class SodaConfig(BaseModel):
    """SODA client configuration."""
    domain: str
    app_token: str
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    user_agent: Optional[str] = None
