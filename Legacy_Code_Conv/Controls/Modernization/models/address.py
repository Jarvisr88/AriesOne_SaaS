from typing import Optional
from pydantic import BaseModel, Field, validator
import re

class Address(BaseModel):
    """
    Address model for handling location information
    Includes validation and formatting capabilities
    """
    address1: str = Field(..., min_length=1, max_length=100, description="Primary address line")
    address2: Optional[str] = Field(None, max_length=100, description="Secondary address line")
    city: str = Field(..., min_length=1, max_length=50, description="City name")
    state: str = Field(..., min_length=2, max_length=2, description="State code (2 letters)")
    zip_code: str = Field(..., min_length=5, max_length=10, description="ZIP/Postal code")
    
    @validator('state')
    def validate_state(cls, v):
        """Validate state code format"""
        if not re.match(r'^[A-Z]{2}$', v):
            raise ValueError('State must be a 2-letter code in uppercase')
        return v
    
    @validator('zip_code')
    def validate_zip(cls, v):
        """Validate ZIP code format"""
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid ZIP code format')
        return v
    
    def to_string(self) -> str:
        """Convert address to formatted string"""
        parts = [self.address1]
        if self.address2:
            parts.append(self.address2)
        parts.append(f"{self.city}, {self.state} {self.zip_code}")
        return "\n".join(parts)
    
    def to_map_string(self) -> str:
        """Convert address to string format suitable for mapping services"""
        return ", ".join(filter(None, [
            self.address1,
            self.address2,
            self.city,
            self.state,
            self.zip_code
        ]))
