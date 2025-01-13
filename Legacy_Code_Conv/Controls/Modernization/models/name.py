from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class Courtesy(str, Enum):
    """Enumeration of standard courtesy titles"""
    MR = "Mr."
    MRS = "Mrs."
    MS = "Ms."
    DR = "Dr."
    PROF = "Prof."

class Name(BaseModel):
    """
    Name model for handling person names
    Includes formatting and validation capabilities
    """
    courtesy: Optional[Courtesy] = Field(None, description="Courtesy title")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    middle_name: Optional[str] = Field(None, max_length=50, description="Middle name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    suffix: Optional[str] = Field(None, max_length=10, description="Name suffix (Jr., Sr., etc.)")
    
    @validator('first_name', 'middle_name', 'last_name', pre=True)
    def capitalize_name(cls, v):
        """Ensure proper capitalization of names"""
        if not v:
            return v
        return " ".join(part.capitalize() for part in v.split())
    
    @validator('suffix')
    def validate_suffix(cls, v):
        """Validate and format name suffix"""
        if not v:
            return v
        common_suffixes = {'JR', 'SR', 'II', 'III', 'IV', 'V'}
        v = v.upper().replace('.', '')
        if v not in common_suffixes:
            raise ValueError('Invalid name suffix')
        return v + '.'
    
    def to_full_name(self) -> str:
        """Convert to full name format"""
        parts = []
        if self.courtesy:
            parts.append(self.courtesy.value)
        parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)
    
    def to_formal_name(self) -> str:
        """Convert to formal name format (last, first)"""
        parts = [self.last_name + ","]
        if self.courtesy:
            parts.append(self.courtesy.value)
        parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name[0] + ".")
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)
