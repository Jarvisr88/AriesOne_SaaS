"""
AbilityCredentials Repository Module
This module provides data access for credentials.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.ability_credentials_model import AbilityCredentials
from ..database.models import CredentialsDB

class AbilityCredentialsRepository:
    """
    Repository for managing credential storage and retrieval.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository.
        
        Args:
            session (AsyncSession): Database session
        """
        self.session = session
    
    async def create(
        self,
        credentials: AbilityCredentials,
        password_hash: bytes,
        password_salt: bytes
    ) -> CredentialsDB:
        """
        Create new credentials in the database.
        
        Args:
            credentials (AbilityCredentials): Credentials to store
            password_hash (bytes): Hashed password
            password_salt (bytes): Salt used for hashing
            
        Returns:
            CredentialsDB: Stored credentials
            
        Raises:
            ValueError: If creation fails
        """
        db_credentials = CredentialsDB(
            sender_id=credentials.sender_id,
            username=credentials.username,
            password_hash=password_hash,
            password_salt=password_salt
        )
        
        self.session.add(db_credentials)
        await self.session.commit()
        await self.session.refresh(db_credentials)
        
        return db_credentials
    
    async def get_by_username(self, username: str) -> Optional[CredentialsDB]:
        """
        Get credentials by username.
        
        Args:
            username (str): Username to look up
            
        Returns:
            Optional[CredentialsDB]: Credentials if found, None otherwise
        """
        query = select(CredentialsDB).where(CredentialsDB.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_sender_id(self, sender_id: str) -> Optional[CredentialsDB]:
        """
        Get credentials by sender ID.
        
        Args:
            sender_id (str): Sender ID to look up
            
        Returns:
            Optional[CredentialsDB]: Credentials if found, None otherwise
        """
        query = select(CredentialsDB).where(CredentialsDB.sender_id == sender_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def update_password(
        self,
        username: str,
        password_hash: bytes,
        password_salt: bytes
    ) -> Optional[CredentialsDB]:
        """
        Update password for existing credentials.
        
        Args:
            username (str): Username to update
            password_hash (bytes): New password hash
            password_salt (bytes): New password salt
            
        Returns:
            Optional[CredentialsDB]: Updated credentials if found
            
        Raises:
            ValueError: If update fails
        """
        credentials = await self.get_by_username(username)
        if not credentials:
            return None
            
        credentials.password_hash = password_hash
        credentials.password_salt = password_salt
        
        await self.session.commit()
        await self.session.refresh(credentials)
        
        return credentials
    
    async def delete(self, username: str) -> bool:
        """
        Delete credentials by username.
        
        Args:
            username (str): Username to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        credentials = await self.get_by_username(username)
        if not credentials:
            return False
            
        await self.session.delete(credentials)
        await self.session.commit()
        
        return True
