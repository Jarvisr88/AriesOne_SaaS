"""
AbilityCredentials Utilities Module
This module provides helper functions for credential management.
"""
from typing import Dict, Any, Optional
import re
from ..models.ability_credentials_model import AbilityCredentials
from ..security.ability_credentials_policy import CredentialsPolicy

def sanitize_username(username: str) -> str:
    """
    Sanitize username input.
    
    Args:
        username (str): Username to sanitize
        
    Returns:
        str: Sanitized username
        
    Raises:
        ValueError: If username is invalid
    """
    # Remove whitespace
    username = username.strip()
    
    # Check against policy
    errors = CredentialsPolicy.validate_username(username)
    if errors:
        raise ValueError("\n".join(errors))
    
    return username

def sanitize_sender_id(sender_id: str) -> str:
    """
    Sanitize sender ID input.
    
    Args:
        sender_id (str): Sender ID to sanitize
        
    Returns:
        str: Sanitized sender ID
        
    Raises:
        ValueError: If sender ID is invalid
    """
    # Remove whitespace
    sender_id = sender_id.strip()
    
    # Check against policy
    errors = CredentialsPolicy.validate_sender_id(sender_id)
    if errors:
        raise ValueError("\n".join(errors))
    
    return sender_id

def create_credential_response(
    credentials: AbilityCredentials,
    include_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Create a safe response dictionary from credentials.
    
    Args:
        credentials (AbilityCredentials): Credentials to format
        include_sensitive (bool): Whether to include sensitive data
        
    Returns:
        Dict[str, Any]: Formatted credential information
    """
    response = {
        "sender_id": credentials.sender_id,
        "username": credentials.username
    }
    
    if include_sensitive:
        response["password"] = "********"  # Never return actual password
    
    return response

def validate_password_strength(password: str) -> Optional[str]:
    """
    Validate password strength and provide feedback.
    
    Args:
        password (str): Password to validate
        
    Returns:
        Optional[str]: Error message if password is weak, None if strong
    """
    errors = CredentialsPolicy.validate_password(password)
    if errors:
        return "\n".join(errors)
    
    # Additional strength checks
    if len(set(password)) < 8:
        return "Password should use more unique characters"
    
    if any(c * 3 in password for c in set(password)):
        return "Password should not contain repeated characters"
    
    return None

def generate_password_requirements() -> Dict[str, Any]:
    """
    Generate human-readable password requirements.
    
    Returns:
        Dict[str, Any]: Password requirements
    """
    return {
        "length": {
            "min": CredentialsPolicy.MIN_PASSWORD_LENGTH,
            "max": CredentialsPolicy.MAX_PASSWORD_LENGTH
        },
        "requirements": {
            "uppercase": "At least one uppercase letter (A-Z)",
            "lowercase": "At least one lowercase letter (a-z)",
            "numbers": "At least one number (0-9)",
            "special": f"At least one special character ({CredentialsPolicy.SPECIAL_CHARS})"
        },
        "recommendations": [
            "Use a mix of different character types",
            "Avoid common words or patterns",
            "Make it memorable but not guessable",
            "Don't reuse passwords from other services"
        ]
    }
