"""
Address Model Module
Defines Pydantic models for address management.
"""
from typing import Optional
from pydantic import BaseModel, Field, validator
import re

class Address(BaseModel):
    """Address data model with validation."""
    
    address_line1: str = Field(
        ...,
        min_length=1,
        max_length=40,
        description="Primary address line"
    )
    address_line2: Optional[str] = Field(
        None,
        max_length=40,
        description="Secondary address line"
    )
    city: str = Field(
        ...,
        min_length=1,
        max_length=25,
        description="City name"
    )
    state: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="State code (2 letters)"
    )
    zip_code: str = Field(
        ...,
        min_length=5,
        max_length=10,
        description="ZIP/Postal code"
    )
    
    @validator('state')
    def validate_state(cls, v):
        """Validate state code format."""
        if not re.match(r'^[A-Z]{2}$', v):
            raise ValueError('State must be 2 uppercase letters')
        return v
    
    @validator('zip_code')
    def validate_zip(cls, v):
        """Validate ZIP code format."""
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid ZIP code format')
        return v

    class Config:
        """Model configuration."""
        schema_extra = {
            "example": {
                "address_line1": "123 Main St",
                "address_line2": "Suite 100",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94105"
            }
        }
