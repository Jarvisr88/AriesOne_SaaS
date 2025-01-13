"""
Name Model Module
Defines Pydantic models for name management.
"""
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, validator

class CourtesyTitle(str, Enum):
    """Enumeration of standard courtesy titles."""
    MR = "Mr."
    MRS = "Mrs."
    MISS = "Miss"
    DR = "Dr."
    REV = "Rev."

class Name(BaseModel):
    """Name data model with validation."""
    
    courtesy_title: Optional[CourtesyTitle] = Field(
        None,
        description="Courtesy title (Mr., Mrs., etc.)"
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="First name"
    )
    middle_initial: Optional[str] = Field(
        None,
        max_length=1,
        description="Middle initial"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Last name"
    )
    suffix: Optional[str] = Field(
        None,
        max_length=4,
        description="Name suffix (Jr., Sr., etc.)"
    )
    
    @validator('middle_initial')
    def validate_middle_initial(cls, v):
        """Validate middle initial format."""
        if v and not v.isalpha():
            raise ValueError('Middle initial must be a single letter')
        return v.upper() if v else v
    
    @validator('suffix')
    def validate_suffix(cls, v):
        """Validate suffix format."""
        if v:
            valid_suffixes = {'Jr.', 'Sr.', 'II', 'III', 'IV'}
            if v not in valid_suffixes:
                raise ValueError(f'Invalid suffix. Must be one of {valid_suffixes}')
        return v

    def full_name(self) -> str:
        """Generate full name string."""
        parts = []
        if self.courtesy_title:
            parts.append(self.courtesy_title.value)
        parts.append(self.first_name)
        if self.middle_initial:
            parts.append(f"{self.middle_initial}.")
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)

    class Config:
        """Model configuration."""
        schema_extra = {
            "example": {
                "courtesy_title": "Mr.",
                "first_name": "John",
                "middle_initial": "A",
                "last_name": "Smith",
                "suffix": "Jr."
            }
        }
