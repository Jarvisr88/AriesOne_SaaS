"""
LineOfBusiness Mapping Module
This module provides mapping functionality between C# and Python implementations.
"""
from typing import Dict, Any
from ..models.line_of_business_model import LineOfBusiness

class LineOfBusinessMapping:
    """
    Mapping class for converting between C# and Python LineOfBusiness implementations.
    Handles the conversion between the C# enum and Python enum while maintaining
    XML serialization compatibility.
    """
    
    @staticmethod
    def from_csharp_xml(xml_str: str) -> LineOfBusiness:
        """
        Convert from C# XML format to Python LineOfBusiness
        
        Args:
            xml_str (str): XML string from C# serialization
            
        Returns:
            LineOfBusiness: Python LineOfBusiness instance
            
        Raises:
            ValueError: If XML is invalid
        """
        return LineOfBusiness.from_xml(xml_str)
    
    @staticmethod
    def to_csharp_xml(line_of_business: LineOfBusiness) -> str:
        """
        Convert from Python LineOfBusiness to C# XML format
        
        Args:
            line_of_business (LineOfBusiness): Python LineOfBusiness instance
            
        Returns:
            str: XML string compatible with C# deserialization
        """
        return line_of_business.to_xml()
