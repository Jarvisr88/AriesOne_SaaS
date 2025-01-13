"""Data encryption module."""
import os
from typing import Any, Optional
from base64 import b64encode, b64decode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel

class EncryptionSettings(BaseModel):
    """Encryption settings."""
    
    SECRET_KEY: str
    SALT: str = "ariesone_salt"  # Should be overridden in production
    ITERATIONS: int = 100_000

class EncryptionService:
    """Service for encrypting and decrypting data."""

    def __init__(self, settings: EncryptionSettings):
        """Initialize encryption service.
        
        Args:
            settings: Encryption settings.
        """
        self.settings = settings
        self._fernet = self._create_fernet()

    def _create_fernet(self) -> Fernet:
        """Create Fernet instance with derived key.
        
        Returns:
            Fernet instance.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.settings.SALT.encode(),
            iterations=self.settings.ITERATIONS,
        )
        key = b64encode(kdf.derive(self.settings.SECRET_KEY.encode()))
        return Fernet(key)

    def encrypt(self, data: Any) -> str:
        """Encrypt data.
        
        Args:
            data: Data to encrypt.
            
        Returns:
            Encrypted data as base64 string.
        """
        if data is None:
            return None
        
        # Convert data to string if not already
        if not isinstance(data, str):
            data = str(data)
        
        encrypted = self._fernet.encrypt(data.encode())
        return b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: Optional[str]) -> Optional[str]:
        """Decrypt data.
        
        Args:
            encrypted_data: Encrypted data as base64 string.
            
        Returns:
            Decrypted data.
        """
        if not encrypted_data:
            return None
        
        try:
            decoded = b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return None

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key.
        
        Returns:
            Base64 encoded key.
        """
        return b64encode(os.urandom(32)).decode()

class EncryptedField:
    """Descriptor for encrypted model fields."""

    def __init__(self, encryption_service: EncryptionService):
        """Initialize encrypted field.
        
        Args:
            encryption_service: Encryption service.
        """
        self.encryption_service = encryption_service
        self.name = None

    def __set_name__(self, owner: Any, name: str) -> None:
        """Set field name.
        
        Args:
            owner: Class that owns this descriptor.
            name: Name of this field.
        """
        self.name = f"_{name}"

    def __get__(self, instance: Any, owner: Any) -> Any:
        """Get decrypted value.
        
        Args:
            instance: Class instance.
            owner: Class that owns this descriptor.
            
        Returns:
            Decrypted value.
        """
        if instance is None:
            return self
        
        encrypted_value = getattr(instance, self.name, None)
        return self.encryption_service.decrypt(encrypted_value)

    def __set__(self, instance: Any, value: Any) -> None:
        """Set encrypted value.
        
        Args:
            instance: Class instance.
            value: Value to encrypt.
        """
        if value is not None:
            encrypted_value = self.encryption_service.encrypt(value)
            setattr(instance, self.name, encrypted_value)
