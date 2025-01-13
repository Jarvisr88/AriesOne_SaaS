"""
AbilityCredentials Policy Module
This module defines security policies for credentials.
"""
from typing import List, Dict
import re

class CredentialsPolicy:
    """
    Defines and enforces security policies for credentials.
    """
    
    # Password complexity requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "@$!%*?&"
    
    # Username requirements
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    ALLOWED_USERNAME_CHARS = r'^[A-Za-z0-9_@.-]+$'
    
    # Sender ID requirements
    MIN_SENDER_LENGTH = 3
    MAX_SENDER_LENGTH = 50
    ALLOWED_SENDER_CHARS = r'^[A-Za-z0-9_-]+$'
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    @classmethod
    def validate_password(cls, password: str) -> List[str]:
        """
        Validate password against security policy.
        
        Args:
            password (str): Password to validate
            
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []
        
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters")
            
        if len(password) > cls.MAX_PASSWORD_LENGTH:
            errors.append(f"Password cannot exceed {cls.MAX_PASSWORD_LENGTH} characters")
            
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
            
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
            
        if cls.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
            
        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARS for c in password):
            errors.append(f"Password must contain at least one special character ({cls.SPECIAL_CHARS})")
            
        return errors
    
    @classmethod
    def validate_username(cls, username: str) -> List[str]:
        """
        Validate username against security policy.
        
        Args:
            username (str): Username to validate
            
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []
        
        if len(username) < cls.MIN_USERNAME_LENGTH:
            errors.append(f"Username must be at least {cls.MIN_USERNAME_LENGTH} characters")
            
        if len(username) > cls.MAX_USERNAME_LENGTH:
            errors.append(f"Username cannot exceed {cls.MAX_USERNAME_LENGTH} characters")
            
        if not re.match(cls.ALLOWED_USERNAME_CHARS, username):
            errors.append("Username contains invalid characters")
            
        return errors
    
    @classmethod
    def validate_sender_id(cls, sender_id: str) -> List[str]:
        """
        Validate sender ID against security policy.
        
        Args:
            sender_id (str): Sender ID to validate
            
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []
        
        if len(sender_id) < cls.MIN_SENDER_LENGTH:
            errors.append(f"Sender ID must be at least {cls.MIN_SENDER_LENGTH} characters")
            
        if len(sender_id) > cls.MAX_SENDER_LENGTH:
            errors.append(f"Sender ID cannot exceed {cls.MAX_SENDER_LENGTH} characters")
            
        if not re.match(cls.ALLOWED_SENDER_CHARS, sender_id):
            errors.append("Sender ID contains invalid characters")
            
        return errors
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Get recommended security headers.
        
        Returns:
            Dict[str, str]: Security headers
        """
        return {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
