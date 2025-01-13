"""
Validation Utilities Module
Provides common validation functions.
"""
import re
from typing import Optional

def validate_zip_code(zip_code: str) -> bool:
    """
    Validate ZIP code format.
    
    Args:
        zip_code: ZIP code to validate
        
    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^\d{5}(-\d{4})?$', zip_code))

def validate_state_code(state: str) -> bool:
    """
    Validate state code format.
    
    Args:
        state: State code to validate
        
    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^[A-Z]{2}$', state))

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Remove non-numeric characters
    digits = re.sub(r'\D', '', phone)
    return len(digits) == 10

def format_phone(phone: str) -> str:
    """
    Format phone number.
    
    Args:
        phone: Phone number to format
        
    Returns:
        Formatted phone number
    """
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_string(text: str) -> str:
    """
    Sanitize string input.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    # Remove special characters
    text = re.sub(r'[^\w\s-]', '', text)
    return text

def format_name(
    first: str,
    last: str,
    middle: Optional[str] = None,
    suffix: Optional[str] = None
) -> str:
    """
    Format full name.
    
    Args:
        first: First name
        last: Last name
        middle: Optional middle name/initial
        suffix: Optional suffix
        
    Returns:
        Formatted full name
    """
    parts = [first]
    if middle:
        if len(middle) == 1:
            parts.append(f"{middle}.")
        else:
            parts.append(middle)
    parts.append(last)
    if suffix:
        parts.append(suffix)
    return " ".join(parts)

def format_address(
    address1: str,
    city: str,
    state: str,
    zip_code: str,
    address2: Optional[str] = None
) -> str:
    """
    Format full address.
    
    Args:
        address1: Primary address line
        city: City name
        state: State code
        zip_code: ZIP code
        address2: Optional secondary address line
        
    Returns:
        Formatted full address
    """
    parts = [address1]
    if address2:
        parts.append(address2)
    parts.append(f"{city}, {state} {zip_code}")
    return "\n".join(parts)
