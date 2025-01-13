"""
DataCenterType Enum Module
This module defines the DataCenterType enum for the application.
Modernized from C# enum in DMEWorks.Ability.Common namespace.
"""
from enum import Enum
from typing import List

class DataCenterType(str, Enum):
    """
    Enumeration of valid data center types.
    Inherits from str to ensure proper serialization.
    
    Attributes:
        CDS: Common Data Service data center
        EDS: Enterprise Data Service data center
    """
    CDS = "CDS"  # Common Data Service
    EDS = "EDS"  # Enterprise Data Service

    @classmethod
    def values(cls) -> List[str]:
        """
        Get all valid data center type values.
        
        Returns:
            List[str]: List of valid data center type values
        """
        return [member.value for member in cls]

    def to_xml(self) -> str:
        """
        Convert to XML format matching C# serialization.
        
        Returns:
            str: XML representation of the data center type
        """
        return f"<DataCenterType>{self.value}</DataCenterType>"

    @classmethod
    def from_xml(cls, xml_str: str) -> "DataCenterType":
        """
        Create DataCenterType from XML string.
        
        Args:
            xml_str (str): XML representation of data center type
            
        Returns:
            DataCenterType: New data center type instance
            
        Raises:
            ValueError: If XML is invalid or value is not a valid data center type
        """
        try:
            # Simple parsing since format is known
            value = xml_str.replace("<DataCenterType>", "").replace("</DataCenterType>", "")
            return cls(value.strip())
        except ValueError as e:
            raise ValueError(f"Invalid data center type XML: {e}")
