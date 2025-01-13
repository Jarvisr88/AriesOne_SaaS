"""
ApplicationName Utilities Module
This module provides utility functions for working with application names.
"""
from typing import Optional
from ..models.application_name_model import ApplicationName

def normalize_application_name(name: str) -> str:
    """
    Normalize an application name string to match enum format.
    
    Args:
        name (str): The application name to normalize
        
    Returns:
        str: The normalized application name
    """
    return name.strip().upper()

def is_valid_application_name(name: str) -> bool:
    """
    Check if a string is a valid application name.
    
    Args:
        name (str): The name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        ApplicationName(normalize_application_name(name))
        return True
    except ValueError:
        return False
