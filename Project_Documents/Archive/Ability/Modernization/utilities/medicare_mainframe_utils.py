"""
MedicareMainframe Utilities Module
This module provides utility functions for Medicare mainframe configuration.
"""
from typing import Optional, Dict, Any
from ..models.medicare_mainframe_model import MedicareMainframe
from ..models.credential_model import Credential
from ..models.application_model import Application

def create_medicare_mainframe(
    application: Optional[Application] = None,
    credential: Optional[Credential] = None,
    clerk_credential: Optional[Credential] = None
) -> MedicareMainframe:
    """
    Create a new MedicareMainframe configuration.
    
    Args:
        application (Optional[Application]): Application configuration
        credential (Optional[Credential]): Primary credential
        clerk_credential (Optional[Credential]): Clerk credential
        
    Returns:
        MedicareMainframe: New configuration instance
    """
    return MedicareMainframe(
        application=application,
        credential=credential,
        clerk_credential=clerk_credential
    )

def validate_configuration(config: MedicareMainframe) -> Dict[str, Any]:
    """
    Validate Medicare mainframe configuration.
    
    Args:
        config (MedicareMainframe): Configuration to validate
        
    Returns:
        Dict[str, Any]: Validation results with any issues found
    """
    issues = []
    
    if config.application_specified and not config.credential_specified:
        issues.append("Application specified but no credential provided")
    
    if config.clerk_credential_specified and not config.credential_specified:
        issues.append("Clerk credential specified but no primary credential provided")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }

def sanitize_configuration(config: MedicareMainframe) -> MedicareMainframe:
    """
    Sanitize Medicare mainframe configuration by cleaning and validating all fields.
    
    Args:
        config (MedicareMainframe): Configuration to sanitize
        
    Returns:
        MedicareMainframe: Sanitized configuration
    """
    return MedicareMainframe(
        application=config.application,
        credential=config.credential,
        clerk_credential=config.clerk_credential
    )

def merge_configurations(
    base: MedicareMainframe,
    override: MedicareMainframe
) -> MedicareMainframe:
    """
    Merge two Medicare mainframe configurations, with override taking precedence.
    
    Args:
        base (MedicareMainframe): Base configuration
        override (MedicareMainframe): Override configuration
        
    Returns:
        MedicareMainframe: Merged configuration
    """
    return MedicareMainframe(
        application=override.application if override.application_specified else base.application,
        credential=override.credential if override.credential_specified else base.credential,
        clerk_credential=override.clerk_credential if override.clerk_credential_specified else base.clerk_credential
    )
