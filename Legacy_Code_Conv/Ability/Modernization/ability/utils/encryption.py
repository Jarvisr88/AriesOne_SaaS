"""
Encryption Module

This module provides encryption utilities for sensitive data.
"""
import base64
from typing import Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config import settings

def _get_encryption_key() -> bytes:
    """Get encryption key from environment."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=settings.ENCRYPTION_SALT.encode(),
        iterations=100000
    )
    key = base64.urlsafe_b64encode(
        kdf.derive(settings.ENCRYPTION_KEY.encode())
    )
    return key

def encrypt_credentials(value: str) -> str:
    """
    Encrypt sensitive credential data.
    
    Args:
        value: Value to encrypt
    
    Returns:
        Encrypted value
    """
    if not value:
        return value

    f = Fernet(_get_encryption_key())
    encrypted = f.encrypt(value.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt_credentials(value: str) -> str:
    """
    Decrypt sensitive credential data.
    
    Args:
        value: Value to decrypt
    
    Returns:
        Decrypted value
    """
    if not value:
        return value

    f = Fernet(_get_encryption_key())
    decrypted = f.decrypt(base64.urlsafe_b64decode(value))
    return decrypted.decode()
