"""
Settings Service Module

This module provides business logic for integration settings.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.settings import IntegrationSettings
from ..repositories.settings_repository import SettingsRepository
from ..utils.encryption import encrypt_credentials, decrypt_credentials
from ..utils.validation import validate_settings

class SettingsService:
    """Service for integration settings management."""

    def __init__(
        self,
        repository: SettingsRepository,
        cache_service = None,
        logger = None
    ):
        """Initialize settings service."""
        self.repository = repository
        self.cache_service = cache_service
        self.logger = logger

    async def create_settings(
        self,
        settings: IntegrationSettings,
        db: AsyncSession
    ) -> IntegrationSettings:
        """
        Create new integration settings.
        
        Args:
            settings: Settings to create
            db: Database session
        
        Returns:
            Created settings
        
        Raises:
            ValueError: If validation fails
        """
        # Validate settings
        validate_settings(settings)

        # Encrypt sensitive data
        settings_encrypted = await self._encrypt_settings(settings)

        # Save to database
        created = await self.repository.create_settings(settings_encrypted, db)

        # Cache if available
        if self.cache_service:
            await self.cache_service.set(
                f"settings:{created.settings_id}",
                created.model_dump(),
                expire=3600
            )

        return created

    async def get_settings(
        self,
        settings_id: UUID,
        db: AsyncSession
    ) -> Optional[IntegrationSettings]:
        """
        Get settings by ID.
        
        Args:
            settings_id: Settings ID
            db: Database session
        
        Returns:
            Settings if found
        """
        # Check cache first
        if self.cache_service:
            cached = await self.cache_service.get(f"settings:{settings_id}")
            if cached:
                return IntegrationSettings.model_validate(cached)

        # Get from database
        settings = await self.repository.get_settings(settings_id, db)
        if not settings:
            return None

        # Decrypt sensitive data
        settings_decrypted = await self._decrypt_settings(settings)

        # Cache if found
        if self.cache_service:
            await self.cache_service.set(
                f"settings:{settings_id}",
                settings_decrypted.model_dump(),
                expire=3600
            )

        return settings_decrypted

    async def update_settings(
        self,
        settings_id: UUID,
        settings: IntegrationSettings,
        db: AsyncSession
    ) -> IntegrationSettings:
        """
        Update settings.
        
        Args:
            settings_id: Settings ID
            settings: Updated settings
            db: Database session
        
        Returns:
            Updated settings
        
        Raises:
            ValueError: If validation fails or settings not found
        """
        # Validate settings
        validate_settings(settings)

        # Check existence
        existing = await self.repository.get_settings(settings_id, db)
        if not existing:
            raise ValueError(f"Settings {settings_id} not found")

        # Encrypt sensitive data
        settings_encrypted = await self._encrypt_settings(settings)

        # Update in database
        updated = await self.repository.update_settings(
            settings_id,
            settings_encrypted,
            db
        )

        # Update cache if available
        if self.cache_service:
            await self.cache_service.delete(f"settings:{settings_id}")
            await self.cache_service.set(
                f"settings:{settings_id}",
                updated.model_dump(),
                expire=3600
            )

        return updated

    async def delete_settings(
        self,
        settings_id: UUID,
        db: AsyncSession
    ) -> None:
        """
        Delete settings.
        
        Args:
            settings_id: Settings ID
            db: Database session
        
        Raises:
            ValueError: If settings not found
        """
        existing = await self.repository.get_settings(settings_id, db)
        if not existing:
            raise ValueError(f"Settings {settings_id} not found")

        await self.repository.delete_settings(settings_id, db)

        # Clear cache if available
        if self.cache_service:
            await self.cache_service.delete(f"settings:{settings_id}")

    async def _encrypt_settings(
        self,
        settings: IntegrationSettings
    ) -> IntegrationSettings:
        """Encrypt sensitive data in settings."""
        if settings.credentials:
            settings.credentials.password = encrypt_credentials(
                settings.credentials.password.get_secret_value()
            )
        if settings.clerk_credentials:
            settings.clerk_credentials.password = encrypt_credentials(
                settings.clerk_credentials.password.get_secret_value()
            )
        if settings.eligibility_credentials:
            settings.eligibility_credentials.password = encrypt_credentials(
                settings.eligibility_credentials.password.get_secret_value()
            )
            settings.eligibility_credentials.api_key = encrypt_credentials(
                settings.eligibility_credentials.api_key.get_secret_value()
            )
        if settings.envelope_credentials:
            settings.envelope_credentials.password = encrypt_credentials(
                settings.envelope_credentials.password.get_secret_value()
            )
        return settings

    async def _decrypt_settings(
        self,
        settings: IntegrationSettings
    ) -> IntegrationSettings:
        """Decrypt sensitive data in settings."""
        if settings.credentials:
            settings.credentials.password = decrypt_credentials(
                settings.credentials.password
            )
        if settings.clerk_credentials:
            settings.clerk_credentials.password = decrypt_credentials(
                settings.clerk_credentials.password
            )
        if settings.eligibility_credentials:
            settings.eligibility_credentials.password = decrypt_credentials(
                settings.eligibility_credentials.password
            )
            settings.eligibility_credentials.api_key = decrypt_credentials(
                settings.eligibility_credentials.api_key
            )
        if settings.envelope_credentials:
            settings.envelope_credentials.password = decrypt_credentials(
                settings.envelope_credentials.password
            )
        return settings
