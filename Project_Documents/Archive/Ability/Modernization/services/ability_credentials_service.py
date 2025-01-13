"""
AbilityCredentials Service Module
This module provides business logic for credential management.
"""
from typing import Optional, Dict, Any
from ..models.ability_credentials_model import AbilityCredentials
from ..security.ability_credentials_encryption import CredentialsEncryption
from ..security.ability_credentials_policy import CredentialsPolicy
from ..repositories.ability_credentials_repository import AbilityCredentialsRepository

class AbilityCredentialsService:
    """
    Service for managing ability credentials.
    Handles authentication, validation, and credential management.
    """
    
    def __init__(self, repository: AbilityCredentialsRepository):
        """
        Initialize the service.
        
        Args:
            repository (AbilityCredentialsRepository): Repository for credential storage
        """
        self.repository = repository
        self.encryption = CredentialsEncryption()
        self.policy = CredentialsPolicy()
    
    async def authenticate(self, credentials: AbilityCredentials) -> Dict[str, Any]:
        """
        Authenticate using provided credentials.
        
        Args:
            credentials (AbilityCredentials): Credentials to authenticate with
            
        Returns:
            Dict[str, Any]: Authentication result with token if successful
            
        Raises:
            ValueError: If authentication fails
        """
        # Validate credentials
        self._validate_credentials(credentials)
        
        # Get stored credentials
        stored = await self.repository.get_by_username(credentials.username)
        if not stored:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not self.encryption.verify_password(
            credentials.password.get_secret_value(),
            stored.password_hash,
            stored.password_salt
        ):
            raise ValueError("Invalid credentials")
        
        # Generate authentication token
        token = await self._generate_token(stored)
        
        return {
            "authenticated": True,
            "token": token,
            "sender_id": stored.sender_id
        }
    
    async def create_credentials(self, credentials: AbilityCredentials) -> Dict[str, Any]:
        """
        Create new credentials.
        
        Args:
            credentials (AbilityCredentials): Credentials to create
            
        Returns:
            Dict[str, Any]: Creation result
            
        Raises:
            ValueError: If validation fails
        """
        # Validate credentials
        self._validate_credentials(credentials)
        
        # Check if username exists
        if await self.repository.get_by_username(credentials.username):
            raise ValueError("Username already exists")
        
        # Hash password
        password_hash, password_salt = self.encryption.hash_password(
            credentials.password.get_secret_value()
        )
        
        # Store credentials
        stored = await self.repository.create(
            credentials,
            password_hash,
            password_salt
        )
        
        return {
            "created": True,
            "sender_id": stored.sender_id,
            "username": stored.username
        }
    
    def _validate_credentials(self, credentials: AbilityCredentials) -> None:
        """
        Validate credentials against security policy.
        
        Args:
            credentials (AbilityCredentials): Credentials to validate
            
        Raises:
            ValueError: If validation fails
        """
        errors = []
        
        # Validate sender ID
        sender_errors = self.policy.validate_sender_id(credentials.sender_id)
        errors.extend(sender_errors)
        
        # Validate username
        username_errors = self.policy.validate_username(credentials.username)
        errors.extend(username_errors)
        
        # Validate password
        password_errors = self.policy.validate_password(
            credentials.password.get_secret_value()
        )
        errors.extend(password_errors)
        
        if errors:
            raise ValueError("\n".join(errors))
    
    async def _generate_token(self, stored_credentials: Any) -> str:
        """
        Generate authentication token.
        
        Args:
            stored_credentials (Any): Stored credential information
            
        Returns:
            str: Authentication token
        """
        # TODO: Implement JWT token generation
        return "dummy_token"  # Placeholder
