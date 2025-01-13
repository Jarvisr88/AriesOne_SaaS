"""
AbilityCredentials Encryption Module
This module provides secure encryption functionality for credentials.
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Tuple

class CredentialsEncryption:
    """
    Handles secure encryption and decryption of credentials.
    Uses Fernet (symmetric encryption) with key derivation.
    """
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Generate a new encryption key.
        
        Returns:
            bytes: New Fernet key
        """
        return Fernet.generate_key()
    
    @staticmethod
    def derive_key(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """
        Derive an encryption key from a password.
        
        Args:
            password (str): Password to derive key from
            salt (bytes, optional): Salt for key derivation
            
        Returns:
            Tuple[bytes, bytes]: (derived key, salt used)
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    @staticmethod
    def encrypt_password(password: str, key: bytes) -> bytes:
        """
        Encrypt a password using Fernet symmetric encryption.
        
        Args:
            password (str): Password to encrypt
            key (bytes): Encryption key
            
        Returns:
            bytes: Encrypted password
        """
        f = Fernet(key)
        return f.encrypt(password.encode())
    
    @staticmethod
    def decrypt_password(encrypted: bytes, key: bytes) -> str:
        """
        Decrypt an encrypted password.
        
        Args:
            encrypted (bytes): Encrypted password
            key (bytes): Decryption key
            
        Returns:
            str: Decrypted password
            
        Raises:
            ValueError: If decryption fails
        """
        try:
            f = Fernet(key)
            return f.decrypt(encrypted).decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt password: {e}")
    
    @staticmethod
    def hash_password(password: str) -> Tuple[bytes, bytes]:
        """
        Create a secure hash of a password for storage.
        
        Args:
            password (str): Password to hash
            
        Returns:
            Tuple[bytes, bytes]: (password hash, salt used)
        """
        salt = os.urandom(16)
        key, _ = CredentialsEncryption.derive_key(password, salt)
        return key, salt
    
    @staticmethod
    def verify_password(password: str, stored_hash: bytes, salt: bytes) -> bool:
        """
        Verify a password against its stored hash.
        
        Args:
            password (str): Password to verify
            stored_hash (bytes): Previously stored hash
            salt (bytes): Salt used for hashing
            
        Returns:
            bool: True if password matches, False otherwise
        """
        key, _ = CredentialsEncryption.derive_key(password, salt)
        return key == stored_hash
