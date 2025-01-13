"""
Name Service Module
Provides business logic for name operations.
"""
import re
from typing import Optional
from ..models.name_model import Name, CourtesyTitle

class NameService:
    """Service for name operations."""
    
    def __init__(self):
        """Initialize name service."""
        self.suffix_pattern = re.compile(r'^(Jr\.|Sr\.|II|III|IV)$')
        
    async def validate_name(self, name: Name) -> Name:
        """
        Validate and standardize name.
        
        Args:
            name: Name to validate
            
        Returns:
            Validated name
            
        Raises:
            ValueError: If name is invalid
        """
        # Validate first name
        if not name.first_name.strip():
            raise ValueError("First name is required")
            
        # Validate last name
        if not name.last_name.strip():
            raise ValueError("Last name is required")
            
        # Standardize format
        return await self.standardize_name(name)
    
    async def standardize_name(self, name: Name) -> Name:
        """
        Standardize name format.
        
        Args:
            name: Name to standardize
            
        Returns:
            Standardized name
        """
        # Convert to title case
        name.first_name = name.first_name.title()
        name.last_name = name.last_name.title()
        
        # Format middle initial
        if name.middle_initial:
            name.middle_initial = name.middle_initial.upper()
            
        # Validate suffix
        if name.suffix and not self.suffix_pattern.match(name.suffix):
            raise ValueError(f"Invalid suffix: {name.suffix}")
            
        return name
    
    async def format_name(self, name: Name, format_type: str = "full") -> str:
        """
        Format name according to specified format.
        
        Args:
            name: Name to format
            format_type: Format type (full, formal, initials)
            
        Returns:
            Formatted name string
        """
        if format_type == "full":
            return name.full_name()
        elif format_type == "formal":
            parts = []
            if name.courtesy_title:
                parts.append(name.courtesy_title.value)
            parts.append(name.last_name)
            return " ".join(parts)
        elif format_type == "initials":
            parts = [name.first_name[0]]
            if name.middle_initial:
                parts.append(name.middle_initial)
            parts.append(name.last_name[0])
            return "".join(parts).upper()
        else:
            raise ValueError(f"Unknown format type: {format_type}")
    
    async def parse_name(self, name_string: str) -> Name:
        """
        Parse name string into structured name.
        
        Args:
            name_string: Full name string to parse
            
        Returns:
            Parsed name object
            
        Raises:
            ValueError: If name cannot be parsed
        """
        # Split name into parts
        parts = name_string.strip().split()
        if len(parts) < 2:
            raise ValueError("Name must include at least first and last name")
            
        # Check for courtesy title
        courtesy_title = None
        if parts[0] in [title.value for title in CourtesyTitle]:
            courtesy_title = CourtesyTitle(parts.pop(0))
            
        # Check for suffix
        suffix = None
        if self.suffix_pattern.match(parts[-1]):
            suffix = parts.pop()
            
        # Parse remaining parts
        if len(parts) == 2:
            first_name, last_name = parts
            middle_initial = None
        elif len(parts) == 3:
            first_name, middle_initial, last_name = parts
            if len(middle_initial) == 1:
                middle_initial = middle_initial.upper()
            else:
                # If middle part is not a single letter, treat it as part of first name
                first_name = f"{first_name} {middle_initial}"
                middle_initial = None
                last_name = parts[2]
        else:
            raise ValueError("Could not parse name format")
            
        return Name(
            courtesy_title=courtesy_title,
            first_name=first_name,
            middle_initial=middle_initial,
            last_name=last_name,
            suffix=suffix
        )
