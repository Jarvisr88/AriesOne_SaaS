"""
DataCenterType Mapping Module
This module provides mapping functionality between C# and Python implementations.
"""
from typing import Dict, Any
from ..models.data_center_type_model import DataCenterType

class DataCenterTypeMapping:
    """
    Mapping class for converting between C# and Python DataCenterType implementations.
    Handles the conversion between the C# enum and Python enum while maintaining
    XML serialization compatibility.
    """
    
    @staticmethod
    def from_csharp_xml(xml_str: str) -> DataCenterType:
        """
        Convert from C# XML format to Python DataCenterType
        
        Args:
            xml_str (str): XML string from C# serialization
            
        Returns:
            DataCenterType: Python DataCenterType instance
            
        Raises:
            ValueError: If XML is invalid
        """
        return DataCenterType.from_xml(xml_str)
    
    @staticmethod
    def to_csharp_xml(data_center_type: DataCenterType) -> str:
        """
        Convert from Python DataCenterType to C# XML format
        
        Args:
            data_center_type (DataCenterType): Python DataCenterType instance
            
        Returns:
            str: XML string compatible with C# deserialization
        """
        return data_center_type.to_xml()
