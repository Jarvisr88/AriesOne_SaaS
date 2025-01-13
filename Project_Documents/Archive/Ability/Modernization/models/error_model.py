"""
Error Model Module
This module defines the Error class for structured error handling.
Modernized from C# class in DMEWorks.Ability.Common namespace.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
import xml.etree.ElementTree as ET
from .error_detail_model import ErrorDetail

class Error(BaseModel):
    """
    Error model for structured error information.
    Provides XML serialization support matching C# implementation.
    """
    code: str = Field(..., description="Error code identifying the error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = Field(default=None, description="Optional additional error details")

    class Config:
        """Pydantic model configuration"""
        allow_population_by_field_name = True

    def to_xml(self) -> str:
        """
        Convert to XML format matching C# serialization.
        
        Returns:
            str: XML representation of the error
        """
        root = ET.Element("error")
        
        code = ET.SubElement(root, "code")
        code.text = self.code
        
        message = ET.SubElement(root, "message")
        message.text = self.message
        
        if self.details:
            details = ET.SubElement(root, "details")
            for detail in self.details:
                details.append(detail.to_xml_element())
        
        return ET.tostring(root, encoding="unicode")

    @classmethod
    def from_xml(cls, xml_str: str) -> "Error":
        """
        Create Error from XML string.
        
        Args:
            xml_str (str): XML representation of error
            
        Returns:
            Error: New error instance
            
        Raises:
            ValueError: If XML is invalid
        """
        try:
            root = ET.fromstring(xml_str)
            if root.tag != "error":
                raise ValueError(f"Invalid error element: {root.tag}")
            
            code = root.find("code")
            message = root.find("message")
            details_elem = root.find("details")
            
            details = []
            if details_elem is not None:
                for detail_elem in details_elem.findall("detail"):
                    details.append(ErrorDetail.from_xml_element(detail_elem))
            
            return cls(
                code=code.text if code is not None else "",
                message=message.text if message is not None else "",
                details=details if details else None
            )
        except ET.ParseError as e:
            raise ValueError(f"Invalid error XML: {e}")
