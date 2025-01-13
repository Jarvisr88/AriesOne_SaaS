"""Encryption utilities for secure credential storage."""

import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def generate_encryption_key() -> bytes:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key()

def derive_key(master_key: bytes, salt: bytes, iterations: int = 100000) -> bytes:
    """Derive an encryption key using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_key))

def encrypt_value(value: str, key: bytes) -> str:
    """Encrypt a value using Fernet symmetric encryption."""
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str, key: bytes) -> str:
    """Decrypt a value using Fernet symmetric encryption."""
    f = Fernet(key)
    return f.decrypt(encrypted_value.encode()).decode()

class KeyVaultClient:
    """Azure Key Vault client for managing encryption keys."""

    def __init__(self, vault_url: str):
        """Initialize Key Vault client."""
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=self.credential)

    async def get_encryption_key(self, key_name: str) -> Optional[bytes]:
        """Get encryption key from Key Vault."""
        try:
            secret = await self.client.get_secret(key_name)
            return base64.urlsafe_b64decode(secret.value)
        except Exception:
            return None

    async def store_encryption_key(self, key_name: str, key: bytes) -> None:
        """Store encryption key in Key Vault."""
        encoded_key = base64.urlsafe_b64encode(key).decode()
        await self.client.set_secret(key_name, encoded_key)

    async def rotate_encryption_key(self, key_name: str) -> bytes:
        """Generate and store new encryption key."""
        new_key = generate_encryption_key()
        await self.store_encryption_key(key_name, new_key)
        return new_key
