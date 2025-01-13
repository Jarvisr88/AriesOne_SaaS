"""
Credential Mapping Module
This module provides mapping functionality between C# and Python implementations.
"""
from typing import Dict, Any
from ..models.credential_model import Credential

class CredentialMapping:
    """
    Mapping class for converting between C# and Python Credential implementations.
    Handles the conversion between the C# class and Python class while maintaining
    XML serialization compatibility.
    """
    
    @staticmethod
    def from_csharp_xml(xml_str: str) -> Credential:
        """
        Convert from C# XML format to Python Credential
        
        Args:
            xml_str (str): XML string from C# serialization
            
        Returns:
            Credential: Python Credential instance
            
        Raises:
            ValueError: If XML is invalid
        """
        return Credential.from_xml(xml_str)
    
    @staticmethod
    def to_csharp_xml(credential: Credential) -> str:
        """
        Convert from Python Credential to C# XML format
        
        Args:
            credential (Credential): Python Credential instance
            
        Returns:
            str: XML string compatible with C# deserialization
        """
        return credential.to_xml()
