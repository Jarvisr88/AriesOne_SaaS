"""
Credential Utilities Module
This module provides utility functions for secure credential handling.
"""
from typing import Optional
from ..models.credential_model import Credential
import hashlib
import base64
import os

def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
    """
    Hash a password using secure hashing algorithm.
    
    Args:
        password (str): Plain text password
        salt (Optional[bytes]): Optional salt for hashing
        
    Returns:
        tuple[str, bytes]: (hashed password, salt used)
    """
    if salt is None:
        salt = os.urandom(16)
    
    # Use SHA-256 with salt
    hasher = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Number of iterations
    )
    
    # Convert to storable format
    hashed = base64.b64encode(hasher).decode('utf-8')
    return hashed, salt

def verify_password(password: str, hashed: str, salt: bytes) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password (str): Plain text password to verify
        hashed (str): Stored hash to verify against
        salt (bytes): Salt used in original hash
        
    Returns:
        bool: True if password matches, False otherwise
    """
    new_hash, _ = hash_password(password, salt)
    return new_hash == hashed

def sanitize_credential(credential: Credential) -> Credential:
    """
    Sanitize a credential by trimming whitespace and normalizing fields.
    
    Args:
        credential (Credential): Credential to sanitize
        
    Returns:
        Credential: Sanitized credential
    """
    return Credential(
        userId=credential.user_id.strip(),
        password=credential.password.get_secret_value()
    )
