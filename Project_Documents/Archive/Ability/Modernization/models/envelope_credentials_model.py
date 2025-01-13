"""
EnvelopeCredentials Model Module
This module defines the EnvelopeCredentials class for envelope-based authentication.
Modernized from C# class in DMEWorks.Ability namespace.
"""
from pydantic import Field, validator
import re
import xml.etree.ElementTree as ET
from .credentials_model import Credentials

class EnvelopeCredentials(Credentials):
    """
    Authentication credentials for envelope-based messaging in the DMEWorks Ability system.
    Extends base Credentials with sender identification.
    
    Attributes:
        sender_id (str): Unique identifier for the sender
        username (str): User's login name (inherited)
        password (SecretStr): User's password (inherited)
    """
    sender_id: str = Field(
        ...,
        alias="sender-id",
        min_length=3,
        max_length=50,
        description="Unique identifier for the sender"
    )

    @validator('sender_id')
    def validate_sender_id(cls, v: str) -> str:
        """Validate sender ID format"""
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError('Sender ID must contain only letters, numbers, underscores, and hyphens')
        return v

    def to_xml(self) -> str:
        """
        Convert to XML format matching C# serialization.
        
        Returns:
            str: XML representation of the credentials
        """
        root = ET.Element("EnvelopeCredentials")
        
        sender_id = ET.SubElement(root, "sender-id")
        sender_id.text = self.sender_id
        
        username = ET.SubElement(root, "username")
        username.text = self.username
        
        password = ET.SubElement(root, "password")
        password.text = self.password.get_secret_value()
        
        return ET.tostring(root, encoding="unicode")

    @classmethod
    def from_xml(cls, xml_str: str) -> "EnvelopeCredentials":
        """
        Create EnvelopeCredentials from XML string.
        
        Args:
            xml_str (str): XML representation of credentials
            
        Returns:
            EnvelopeCredentials: New credentials instance
            
        Raises:
            ValueError: If XML is invalid
        """
        try:
            root = ET.fromstring(xml_str)
            return cls(
                sender_id=root.find("sender-id").text,
                username=root.find("username").text,
                password=root.find("password").text
            )
        except (ET.ParseError, AttributeError) as e:
            raise ValueError(f"Invalid envelope credentials XML: {e}")

    def get_redacted_dict(self) -> dict:
        """
        Get a dictionary representation with sensitive data redacted.
        
        Returns:
            dict: Redacted credential information
        """
        return {
            "sender_id": self.sender_id,
            "username": self.username,
            "password": "********"
        }
