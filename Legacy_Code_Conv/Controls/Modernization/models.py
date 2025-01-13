"""
Models for the Controls module.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class AddressType(str, Enum):
    """Address type enumeration."""
    HOME = "home"
    WORK = "work"
    DELIVERY = "delivery"
    BILLING = "billing"
    OTHER = "other"

class Address(BaseModel):
    """Address model with validation."""
    street1: str = Field(..., min_length=1, max_length=100)
    street2: Optional[str] = Field(None, max_length=100)
    city: str = Field(..., min_length=1, max_length=50)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., regex=r'^\d{5}(-\d{4})?$')
    type: AddressType
    is_primary: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    validated: bool = False
    validation_date: Optional[datetime] = None
    
    @validator('state')
    def validate_state(cls, v):
        """Validate state code."""
        if v.upper() not in US_STATES:
            raise ValueError('Invalid state code')
        return v.upper()
    
    @validator('zip_code')
    def validate_zip(cls, v):
        """Validate ZIP code format."""
        if not ZIP_CODE_PATTERN.match(v):
            raise ValueError('Invalid ZIP code format')
        return v

class NameFormat(BaseModel):
    """Name formatting model."""
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    suffix: Optional[str] = Field(None, max_length=10)
    prefix: Optional[str] = Field(None, max_length=10)
    
    def format_full(self) -> str:
        """Format full name."""
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return ' '.join(parts)
    
    def format_last_first(self) -> str:
        """Format name as 'last, first middle'."""
        parts = [self.last_name + ',', self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)

class ChangeTracker(BaseModel):
    """Change tracking model."""
    field_name: str
    old_value: Any
    new_value: Any
    changed_by: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ValidationResult(BaseModel):
    """Validation result model."""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []
    metadata: Dict[str, Any] = {}
