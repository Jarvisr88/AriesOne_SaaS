"""
Validation Module

This module provides validation utilities for settings.
"""
from typing import Optional

from pydantic import ValidationError

from ..models.settings import IntegrationSettings

def validate_settings(settings: IntegrationSettings) -> None:
    """
    Validate integration settings.
    
    Args:
        settings: Settings to validate
    
    Raises:
        ValueError: If validation fails
    """
    try:
        # Validate credentials if provided
        if settings.credentials:
            _validate_credentials(settings.credentials)

        # Validate clerk credentials if provided
        if settings.clerk_credentials:
            _validate_clerk_credentials(settings.clerk_credentials)

        # Validate eligibility credentials if provided
        if settings.eligibility_credentials:
            _validate_eligibility_credentials(settings.eligibility_credentials)

        # Validate envelope credentials if provided
        if settings.envelope_credentials:
            _validate_envelope_credentials(settings.envelope_credentials)

    except ValidationError as e:
        raise ValueError(f"Settings validation failed: {str(e)}")

def _validate_credentials(credentials) -> None:
    """
    Validate base credentials.
    
    Args:
        credentials: Credentials to validate
    
    Raises:
        ValueError: If validation fails
    """
    if not credentials.sender_id:
        raise ValueError("Sender ID is required")
    if not credentials.username:
        raise ValueError("Username is required")
    if not credentials.password:
        raise ValueError("Password is required")

def _validate_clerk_credentials(credentials) -> None:
    """
    Validate clerk credentials.
    
    Args:
        credentials: Credentials to validate
    
    Raises:
        ValueError: If validation fails
    """
    _validate_credentials(credentials)
    if not credentials.clerk_id:
        raise ValueError("Clerk ID is required")
    if not credentials.role:
        raise ValueError("Role is required")

def _validate_eligibility_credentials(credentials) -> None:
    """
    Validate eligibility credentials.
    
    Args:
        credentials: Credentials to validate
    
    Raises:
        ValueError: If validation fails
    """
    _validate_credentials(credentials)
    if not credentials.facility_id:
        raise ValueError("Facility ID is required")
    if not credentials.api_key:
        raise ValueError("API key is required")

def _validate_envelope_credentials(credentials) -> None:
    """
    Validate envelope credentials.
    
    Args:
        credentials: Credentials to validate
    
    Raises:
        ValueError: If validation fails
    """
    _validate_credentials(credentials)
    if not credentials.envelope_id:
        raise ValueError("Envelope ID is required")
    if credentials.environment not in ["production", "staging"]:
        raise ValueError("Invalid environment")
