"""
Map Model Module
Defines Pydantic models for map provider integration.
"""
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from .address_model import Address

class MapProvider(str, Enum):
    """Supported map providers."""
    GOOGLE = "google"
    BING = "bing"
    OPENSTREETMAP = "openstreetmap"

class MapCoordinates(BaseModel):
    """Geographic coordinates model."""
    
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude coordinate"
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude coordinate"
    )

class MapLocation(BaseModel):
    """Location model with address and coordinates."""
    
    address: Address
    coordinates: Optional[MapCoordinates] = None
    formatted_address: Optional[str] = None
    place_id: Optional[str] = None

class MapProviderConfig(BaseModel):
    """Map provider configuration."""
    
    provider: MapProvider
    api_key: Optional[str] = Field(None, description="Provider API key")
    base_url: HttpUrl
    enabled: bool = True

class MapSearchResult(BaseModel):
    """Map search result model."""
    
    location: MapLocation
    provider: MapProvider
    confidence_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Search result confidence score"
    )
    alternatives: List[MapLocation] = []

    class Config:
        """Model configuration."""
        schema_extra = {
            "example": {
                "location": {
                    "address": {
                        "address_line1": "123 Main St",
                        "city": "San Francisco",
                        "state": "CA",
                        "zip_code": "94105"
                    },
                    "coordinates": {
                        "latitude": 37.7749,
                        "longitude": -122.4194
                    },
                    "formatted_address": "123 Main St, San Francisco, CA 94105"
                },
                "provider": "google",
                "confidence_score": 0.95,
                "alternatives": []
            }
        }
