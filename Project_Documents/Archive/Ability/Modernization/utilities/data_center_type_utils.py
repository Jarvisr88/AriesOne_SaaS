"""
DataCenterType Utilities Module
This module provides utility functions for working with data center types.
"""
from typing import Optional
from ..models.data_center_type_model import DataCenterType

def is_valid_data_center_type(value: str) -> bool:
    """
    Check if a string represents a valid data center type.
    
    Args:
        value (str): Value to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        DataCenterType(value.upper())
        return True
    except ValueError:
        return False

def normalize_data_center_type(value: str) -> str:
    """
    Normalize a data center type string.
    
    Args:
        value (str): Value to normalize
        
    Returns:
        str: Normalized value
        
    Raises:
        ValueError: If value is not a valid data center type
    """
    normalized = value.strip().upper()
    if not is_valid_data_center_type(normalized):
        raise ValueError(f"Invalid data center type: {value}")
    return normalized

def get_data_center_type(value: str) -> Optional[DataCenterType]:
    """
    Get DataCenterType enum value from string if valid.
    
    Args:
        value (str): String value to convert
        
    Returns:
        Optional[DataCenterType]: DataCenterType if valid, None otherwise
    """
    try:
        return DataCenterType(normalize_data_center_type(value))
    except ValueError:
        return None
