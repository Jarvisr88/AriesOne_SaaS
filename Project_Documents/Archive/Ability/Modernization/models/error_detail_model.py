"""
ErrorDetail Model Module
This module defines the ErrorDetail class for detailed error information.
Modernized from C# class in DMEWorks.Ability.Common namespace.
"""
from pydantic import BaseModel, Field
from typing import Optional
import xml.etree.ElementTree as ET

class ErrorDetail(BaseModel):
    """
    Error detail model for key-value pair error information.
    Provides XML serialization support matching C# implementation.
    """
    key: str = Field(..., description="Key identifying the error detail")
    value: str = Field(..., description="Value providing detail information")

    class Config:
        """Pydantic model configuration"""
        allow_population_by_field_name = True

    def to_xml_element(self) -> ET.Element:
        """
        Convert to XML element matching C# serialization.
        
        Returns:
            ET.Element: XML element representation
        """
        element = ET.Element("detail")
        element.set("key", self.key)
        element.set("value", self.value)
        return element

    @classmethod
    def from_xml_element(cls, element: ET.Element) -> "ErrorDetail":
        """
        Create ErrorDetail from XML element.
        
        Args:
            element (ET.Element): XML element to parse
            
        Returns:
            ErrorDetail: New error detail instance
            
        Raises:
            ValueError: If XML element is invalid
        """
        if element.tag != "detail":
            raise ValueError(f"Invalid error detail element: {element.tag}")
        
        return cls(
            key=element.get("key", ""),
            value=element.get("value", "")
        )
