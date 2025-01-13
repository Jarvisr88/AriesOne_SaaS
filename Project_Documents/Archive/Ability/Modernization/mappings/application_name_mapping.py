"""
ApplicationName Mapping Module
This module provides mapping functionality between C# and Python implementations.
"""
from typing import Dict, Any
from ..models.application_name_model import ApplicationName

class ApplicationNameMapping:
    """
    Mapping class for converting between C# and Python ApplicationName implementations.
    Handles the conversion between the C# enum and Python enum while maintaining
    XML serialization compatibility.
    """
    
    @staticmethod
    def from_csharp(value: str) -> ApplicationName:
        """
        Convert from C# enum value to Python enum
        
        Args:
            value (str): C# enum value
            
        Returns:
            ApplicationName: Corresponding Python enum value
            
        Raises:
            ValueError: If the value is not a valid application name
        """
        return ApplicationName(value.upper())
    
    @staticmethod
    def to_csharp(value: ApplicationName) -> str:
        """
        Convert from Python enum to C# enum value
        
        Args:
            value (ApplicationName): Python enum value
            
        Returns:
            str: Corresponding C# enum value
        """
        return value.value
