"""
LineOfBusiness Utilities Module
This module provides utility functions for working with lines of business.
"""
from typing import Optional, Dict, List
from ..models.line_of_business_model import LineOfBusiness

def is_valid_line_of_business(value: str) -> bool:
    """
    Check if a string represents a valid line of business.
    
    Args:
        value (str): Value to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        LineOfBusiness(value)
        return True
    except ValueError:
        return False

def normalize_line_of_business(value: str) -> str:
    """
    Normalize a line of business string.
    
    Args:
        value (str): Value to normalize
        
    Returns:
        str: Normalized value
        
    Raises:
        ValueError: If value is not a valid line of business
    """
    normalized = value.strip()
    if not is_valid_line_of_business(normalized):
        raise ValueError(f"Invalid line of business: {value}")
    return normalized

def get_line_of_business_description(lob: LineOfBusiness) -> str:
    """
    Get the description for a line of business.
    
    Args:
        lob (LineOfBusiness): Line of business
        
    Returns:
        str: Description of the line of business
    """
    return LineOfBusiness.descriptions()[lob.value]

def get_medicare_lines_of_business() -> List[LineOfBusiness]:
    """
    Get all Medicare-related lines of business.
    
    Returns:
        List[LineOfBusiness]: List of Medicare-related lines of business
    """
    return [
        LineOfBusiness.PART_A,
        LineOfBusiness.PART_B,
        LineOfBusiness.HHH,
        LineOfBusiness.DME
    ]

def get_specialty_lines_of_business() -> List[LineOfBusiness]:
    """
    Get all specialty lines of business.
    
    Returns:
        List[LineOfBusiness]: List of specialty lines of business
    """
    return [
        LineOfBusiness.RURAL_HEALTH,
        LineOfBusiness.FQHC,
        LineOfBusiness.SECTION_1011,
        LineOfBusiness.MUTUAL,
        LineOfBusiness.INDIAN_HEALTH
    ]
