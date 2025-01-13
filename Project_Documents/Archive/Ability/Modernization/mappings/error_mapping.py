"""
Error Mapping Module
This module provides mapping functionality between C# and Python implementations.
"""
from typing import Dict, Any
from ..models.error_model import Error
from ..models.error_detail_model import ErrorDetail

class ErrorMapping:
    """
    Mapping class for converting between C# and Python Error implementations.
    Handles the conversion between C# classes and Python classes while maintaining
    XML serialization compatibility.
    """
    
    @staticmethod
    def from_csharp_xml(xml_str: str) -> Error:
        """
        Convert from C# XML format to Python Error
        
        Args:
            xml_str (str): XML string from C# serialization
            
        Returns:
            Error: Python Error instance
            
        Raises:
            ValueError: If XML is invalid
        """
        return Error.from_xml(xml_str)
    
    @staticmethod
    def to_csharp_xml(error: Error) -> str:
        """
        Convert from Python Error to C# XML format
        
        Args:
            error (Error): Python Error instance
            
        Returns:
            str: XML string compatible with C# deserialization
        """
        return error.to_xml()
