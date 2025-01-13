"""
Validation Module

This module provides validation utilities for common operations.
"""
from typing import Optional

from pydantic import ValidationError

from ..models.common_models import Application, Error

def validate_application(application: Application) -> None:
    """
    Validate application configuration.
    
    Args:
        application: Application to validate
    
    Raises:
        ValueError: If validation fails
    """
    try:
        # Validate facility state
        if not _is_valid_state_code(application.facility_state):
            raise ValueError("Invalid facility state code")

        # Validate PPTN region if provided
        if application.pptn_region and not _is_valid_pptn_region(application.pptn_region):
            raise ValueError("Invalid PPTN region")

        # Additional validation rules can be added here

    except ValidationError as e:
        raise ValueError(f"Application validation failed: {str(e)}")

def validate_error(error: Error) -> None:
    """
    Validate error log.
    
    Args:
        error: Error to validate
    
    Raises:
        ValueError: If validation fails
    """
    try:
        # Validate severity
        if error.severity not in ["debug", "info", "warning", "error", "critical"]:
            raise ValueError("Invalid error severity")

        # Validate source
        if not error.source:
            raise ValueError("Error source is required")

        # Validate message
        if not error.message:
            raise ValueError("Error message is required")

        # Additional validation rules can be added here

    except ValidationError as e:
        raise ValueError(f"Error validation failed: {str(e)}")

def _is_valid_state_code(state_code: str) -> bool:
    """
    Validate US state code.
    
    Args:
        state_code: Two-letter state code
    
    Returns:
        bool indicating if state code is valid
    """
    valid_states = {
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
        "DC", "PR", "VI", "GU", "MP", "AS"
    }
    return state_code.upper() in valid_states

def _is_valid_pptn_region(region: str) -> bool:
    """
    Validate PPTN region code.
    
    Args:
        region: PPTN region code
    
    Returns:
        bool indicating if region code is valid
    """
    valid_regions = {"EAST", "WEST", "NORTH", "SOUTH", "CENTRAL"}
    return region.upper() in valid_regions
