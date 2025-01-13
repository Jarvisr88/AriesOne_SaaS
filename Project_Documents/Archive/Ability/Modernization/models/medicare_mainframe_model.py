"""
MedicareMainframe Model Module
This module defines the MedicareMainframe class for Medicare mainframe configuration.
Modernized from C# class in DMEWorks.Ability.Common namespace.
"""
from pydantic import BaseModel, Field
from typing import Optional
import xml.etree.ElementTree as ET
from .application_model import Application
from .credential_model import Credential

class MedicareMainframe(BaseModel):
    """
    Medicare mainframe configuration model.
    Provides configuration and credentials for Medicare mainframe access.
    
    Attributes:
        application (Optional[Application]): Application configuration
        credential (Optional[Credential]): Primary credential
        clerk_credential (Optional[Credential]): Clerk-specific credential
    """
    application: Optional[Application] = Field(
        default=None,
        description="Application configuration for mainframe access"
    )
    credential: Optional[Credential] = Field(
        default=None,
        description="Primary credential for mainframe access"
    )
    clerk_credential: Optional[Credential] = Field(
        default=None,
        alias="clerkCredential",
        description="Clerk-specific credential for specialized operations"
    )

    class Config:
        """Pydantic model configuration"""
        allow_population_by_field_name = True

    @property
    def application_specified(self) -> bool:
        """Check if application is specified"""
        return self.application is not None

    @property
    def credential_specified(self) -> bool:
        """Check if credential is specified"""
        return self.credential is not None

    @property
    def clerk_credential_specified(self) -> bool:
        """Check if clerk credential is specified"""
        return self.clerk_credential is not None

    def to_xml(self) -> str:
        """
        Convert to XML format matching C# serialization.
        
        Returns:
            str: XML representation of the configuration
        """
        root = ET.Element("MedicareMainframe")
        
        if self.application_specified:
            app_elem = ET.fromstring(self.application.to_xml())
            app_elem.tag = "application"
            root.append(app_elem)
        
        if self.credential_specified:
            cred_elem = ET.fromstring(self.credential.to_xml())
            cred_elem.tag = "credential"
            root.append(cred_elem)
        
        if self.clerk_credential_specified:
            clerk_elem = ET.fromstring(self.clerk_credential.to_xml())
            clerk_elem.tag = "clerkCredential"
            root.append(clerk_elem)
        
        return ET.tostring(root, encoding="unicode")

    @classmethod
    def from_xml(cls, xml_str: str) -> "MedicareMainframe":
        """
        Create MedicareMainframe from XML string.
        
        Args:
            xml_str (str): XML representation of configuration
            
        Returns:
            MedicareMainframe: New configuration instance
            
        Raises:
            ValueError: If XML is invalid
        """
        try:
            root = ET.fromstring(xml_str)
            if root.tag != "MedicareMainframe":
                raise ValueError(f"Invalid root element: {root.tag}")
            
            app_elem = root.find("application")
            cred_elem = root.find("credential")
            clerk_elem = root.find("clerkCredential")
            
            return cls(
                application=Application.from_xml(ET.tostring(app_elem, encoding="unicode"))
                    if app_elem is not None else None,
                credential=Credential.from_xml(ET.tostring(cred_elem, encoding="unicode"))
                    if cred_elem is not None else None,
                clerk_credential=Credential.from_xml(ET.tostring(clerk_elem, encoding="unicode"))
                    if clerk_elem is not None else None
            )
        except ET.ParseError as e:
            raise ValueError(f"Invalid Medicare mainframe XML: {e}")
