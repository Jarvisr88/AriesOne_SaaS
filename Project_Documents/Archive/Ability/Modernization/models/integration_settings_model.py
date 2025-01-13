"""
IntegrationSettings Model Module
This module defines the IntegrationSettings class for managing integration configuration.
Modernized from C# class in DMEWorks.Ability namespace.
"""
from pydantic import BaseModel, Field
from typing import Optional
import xml.etree.ElementTree as ET
from .credentials_model import Credentials
from .ability_credentials_model import AbilityCredentials
from .envelope_credentials_model import EnvelopeCredentials

class IntegrationSettings(BaseModel):
    """
    Configuration settings for DMEWorks Ability system integration.
    Manages various types of credentials and provides XML serialization.
    
    Attributes:
        credentials (Optional[Credentials]): Basic system credentials
        clerk_credentials (Optional[Credentials]): Clerk-specific credentials
        eligibility_credentials (Optional[AbilityCredentials]): Eligibility-specific credentials
        envelope_credentials (Optional[EnvelopeCredentials]): Envelope-specific credentials
    """
    credentials: Optional[Credentials] = Field(
        None,
        description="Basic system credentials"
    )
    clerk_credentials: Optional[Credentials] = Field(
        None,
        alias="clerk-credentials",
        description="Clerk-specific credentials"
    )
    eligibility_credentials: Optional[AbilityCredentials] = Field(
        None,
        alias="eligibility-credentials",
        description="Eligibility-specific credentials"
    )
    envelope_credentials: Optional[EnvelopeCredentials] = Field(
        None,
        alias="envelope-credentials",
        description="Envelope-specific credentials"
    )

    class Config:
        """Pydantic model configuration"""
        allow_population_by_field_name = True

    @classmethod
    def from_xml(cls, xml_str: str) -> "IntegrationSettings":
        """
        Create IntegrationSettings from XML string.
        
        Args:
            xml_str (str): XML settings data
            
        Returns:
            IntegrationSettings: New settings instance
            
        Raises:
            ValueError: If XML is invalid
        """
        try:
            root = ET.fromstring(xml_str or "")
            if not xml_str:
                return cls()

            settings = {}
            
            # Parse basic credentials
            cred_elem = root.find("credentials")
            if cred_elem is not None:
                settings["credentials"] = Credentials.from_xml(
                    ET.tostring(cred_elem, encoding="unicode")
                )
            
            # Parse clerk credentials
            clerk_elem = root.find("clerk-credentials")
            if clerk_elem is not None:
                settings["clerk_credentials"] = Credentials.from_xml(
                    ET.tostring(clerk_elem, encoding="unicode")
                )
            
            # Parse eligibility credentials
            elig_elem = root.find("eligibility-credentials")
            if elig_elem is not None:
                settings["eligibility_credentials"] = AbilityCredentials.from_xml(
                    ET.tostring(elig_elem, encoding="unicode")
                )
            
            # Parse envelope credentials
            env_elem = root.find("envelope-credentials")
            if env_elem is not None:
                settings["envelope_credentials"] = EnvelopeCredentials.from_xml(
                    ET.tostring(env_elem, encoding="unicode")
                )
            
            return cls(**settings)
            
        except Exception as e:
            raise ValueError(f"Failed to parse settings XML: {e}")

    def to_xml(self) -> str:
        """
        Convert to XML format matching C# serialization.
        
        Returns:
            str: XML representation of settings
        """
        root = ET.Element("settings")
        
        # Add basic credentials
        if self.credentials:
            cred_elem = ET.fromstring(self.credentials.to_xml())
            root.append(cred_elem)
        
        # Add clerk credentials
        if self.clerk_credentials:
            clerk_elem = ET.fromstring(self.clerk_credentials.to_xml())
            clerk_elem.tag = "clerk-credentials"
            root.append(clerk_elem)
        
        # Add eligibility credentials
        if self.eligibility_credentials:
            elig_elem = ET.fromstring(self.eligibility_credentials.to_xml())
            elig_elem.tag = "eligibility-credentials"
            root.append(elig_elem)
        
        # Add envelope credentials
        if self.envelope_credentials:
            env_elem = ET.fromstring(self.envelope_credentials.to_xml())
            env_elem.tag = "envelope-credentials"
            root.append(env_elem)
        
        return ET.tostring(root, encoding="unicode", xml_declaration=False)
