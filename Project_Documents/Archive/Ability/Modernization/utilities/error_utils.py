"""
Error Utilities Module
This module provides utility functions for error handling and creation.
"""
from typing import List, Optional, Dict, Any
from ..models.error_model import Error
from ..models.error_detail_model import ErrorDetail

def create_error(code: str, message: str, details: Optional[Dict[str, str]] = None) -> Error:
    """
    Create a new Error instance with optional details.
    
    Args:
        code (str): Error code
        message (str): Error message
        details (Optional[Dict[str, str]]): Optional key-value pairs for error details
        
    Returns:
        Error: New error instance
    """
    error_details = None
    if details:
        error_details = [
            ErrorDetail(key=k, value=str(v))
            for k, v in details.items()
        ]
    
    return Error(
        code=code,
        message=message,
        details=error_details
    )

def format_error_message(error: Error) -> str:
    """
    Format error into human-readable message.
    
    Args:
        error (Error): Error to format
        
    Returns:
        str: Formatted error message
    """
    message = f"Error {error.code}: {error.message}"
    if error.details:
        details = "; ".join(f"{d.key}: {d.value}" for d in error.details)
        message += f" ({details})"
    return message

def sanitize_error(error: Error) -> Error:
    """
    Sanitize error by trimming whitespace and normalizing fields.
    
    Args:
        error (Error): Error to sanitize
        
    Returns:
        Error: Sanitized error
    """
    details = None
    if error.details:
        details = [
            ErrorDetail(
                key=detail.key.strip(),
                value=detail.value.strip()
            )
            for detail in error.details
        ]
    
    return Error(
        code=error.code.strip(),
        message=error.message.strip(),
        details=details
    )
