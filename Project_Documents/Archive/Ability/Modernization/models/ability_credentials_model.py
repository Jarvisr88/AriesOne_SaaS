"""
AbilityCredentials Model Module
This module defines the AbilityCredentials class for authentication.
Modernized from C# class in DMEWorks.Ability namespace.
"""
from pydantic import BaseModel, Field, SecretStr, validator
import re
from typing import Optional
import xml.etree.ElementTree as ET

class AbilityCredentials(BaseModel):
    """
    Authentication credentials for the DMEWorks Ability system.
    Provides secure storage and handling of authentication information.
    
    Attributes:
        sender_id (str): Unique identifier for the sender
        username (str): User's login name
        password (SecretStr): User's password, stored securely
    """
    sender_id: str = Field(
        ...,
        alias="sender-id",
        min_length=3,
        max_length=50,
        description="Unique identifier for the sender"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="User's login name"
    )
    password: SecretStr = Field(
        ...,
        description="User's password"
    )

    class Config:
        """Pydantic model configuration"""
        allow_population_by_field_name = True
        
    @validator('sender_id')
    def validate_sender_id(cls, v: str) -> str:
        """Validate sender ID format"""
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError('Sender ID must contain only letters, numbers, underscores, and hyphens')
        return v
    
    @validator('username')
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not re.match(r'^[A-Za-z0-9_@.-]+$', v):
            raise ValueError('Username must contain only letters, numbers, and common symbols')
        return v
    
    @validator('password')
    def validate_password(cls, v: SecretStr) -> SecretStr:
        """Validate password complexity"""
        password = v.get_secret_value()
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$', password):
            raise ValueError('Password must contain uppercase, lowercase, number, and special character')
        return v

    def to_xml(self) -> str:
        """
        Convert to XML format matching C# serialization.
        
        Returns:
            str: XML representation of the credentials
        """
        root = ET.Element("AbilityCredentials")
        
        sender_id = ET.SubElement(root, "sender-id")
        sender_id.text = self.sender_id
        
        username = ET.SubElement(root, "username")
        username.text = self.username
        
        password = ET.SubElement(root, "password")
        password.text = self.password.get_secret_value()
        
        return ET.tostring(root, encoding="unicode")

    @classmethod
    def from_xml(cls, xml_str: str) -> "AbilityCredentials":
        """
        Create AbilityCredentials from XML string.
        
        Args:
            xml_str (str): XML representation of credentials
            
        Returns:
            AbilityCredentials: New credentials instance
            
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
            raise ValueError(f"Invalid credentials XML: {e}")

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
