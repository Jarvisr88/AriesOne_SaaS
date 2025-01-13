"""
Credential Model Module
This module defines the Credential class for secure user authentication.
Modernized from C# class in DMEWorks.Ability.Common namespace.
"""
from pydantic import BaseModel, Field, SecretStr
from typing import Optional
import xml.etree.ElementTree as ET

class Credential(BaseModel):
    """
    Credential model for user authentication.
    Provides secure storage and serialization of user credentials.
    """
    user_id: str = Field(..., alias="userId")
    password: SecretStr = Field(..., alias="password")

    class Config:
        """Pydantic model configuration"""
        allow_population_by_field_name = True

    def to_xml(self) -> str:
        """
        Convert credential to XML format matching C# serialization.
        
        Returns:
            str: XML representation of the credential
        """
        root = ET.Element("Credential")
        user_id = ET.SubElement(root, "userId")
        user_id.text = self.user_id
        password = ET.SubElement(root, "password")
        password.text = self.password.get_secret_value()
        return ET.tostring(root, encoding="unicode")

    @classmethod
    def from_xml(cls, xml_str: str) -> "Credential":
        """
        Create credential from XML string.
        
        Args:
            xml_str (str): XML representation of credential
            
        Returns:
            Credential: New credential instance
            
        Raises:
            ValueError: If XML is invalid
        """
        try:
            root = ET.fromstring(xml_str)
            return cls(
                userId=root.find("userId").text,
                password=root.find("password").text
            )
        except (ET.ParseError, AttributeError) as e:
            raise ValueError(f"Invalid credential XML: {e}")
