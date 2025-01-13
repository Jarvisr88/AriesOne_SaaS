"""
Settings Repository Module

This module provides data access for integration settings.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.settings import IntegrationSettings
from ..models.database.ability_models import (
    IntegrationSettingsDB,
    CredentialsDB,
    ClerkCredentialsDB,
    EligibilityCredentialsDB,
    EnvelopeCredentialsDB
)

class SettingsRepository:
    """Repository for settings data access."""

    async def create_settings(
        self,
        settings: IntegrationSettings,
        db: AsyncSession
    ) -> IntegrationSettings:
        """
        Create new settings.
        
        Args:
            settings: Settings to create
            db: Database session
        
        Returns:
            Created settings
        """
        # Create credentials if provided
        credentials_id = None
        if settings.credentials:
            cred_db = CredentialsDB(
                sender_id=settings.credentials.sender_id,
                username=settings.credentials.username,
                password=settings.credentials.password.get_secret_value()
            )
            db.add(cred_db)
            await db.flush()
            credentials_id = cred_db.credential_id

        # Create clerk credentials if provided
        clerk_credentials_id = None
        if settings.clerk_credentials:
            clerk_db = ClerkCredentialsDB(
                sender_id=settings.clerk_credentials.sender_id,
                username=settings.clerk_credentials.username,
                password=settings.clerk_credentials.password.get_secret_value(),
                clerk_id=settings.clerk_credentials.clerk_id,
                role=settings.clerk_credentials.role,
                permissions=settings.clerk_credentials.permissions
            )
            db.add(clerk_db)
            await db.flush()
            clerk_credentials_id = clerk_db.credential_id

        # Create eligibility credentials if provided
        eligibility_credentials_id = None
        if settings.eligibility_credentials:
            elig_db = EligibilityCredentialsDB(
                sender_id=settings.eligibility_credentials.sender_id,
                username=settings.eligibility_credentials.username,
                password=settings.eligibility_credentials.password.get_secret_value(),
                facility_id=settings.eligibility_credentials.facility_id,
                api_key=settings.eligibility_credentials.api_key.get_secret_value()
            )
            db.add(elig_db)
            await db.flush()
            eligibility_credentials_id = elig_db.credential_id

        # Create envelope credentials if provided
        envelope_credentials_id = None
        if settings.envelope_credentials:
            env_db = EnvelopeCredentialsDB(
                sender_id=settings.envelope_credentials.sender_id,
                username=settings.envelope_credentials.username,
                password=settings.envelope_credentials.password.get_secret_value(),
                envelope_id=settings.envelope_credentials.envelope_id,
                environment=settings.envelope_credentials.environment
            )
            db.add(env_db)
            await db.flush()
            envelope_credentials_id = env_db.credential_id

        # Create settings
        settings_db = IntegrationSettingsDB(
            settings_id=settings.settings_id,
            credentials_id=credentials_id,
            clerk_credentials_id=clerk_credentials_id,
            eligibility_credentials_id=eligibility_credentials_id,
            envelope_credentials_id=envelope_credentials_id
        )

        db.add(settings_db)
        await db.commit()
        await db.refresh(settings_db)

        return await self._convert_to_model(settings_db, db)

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
        stmt = select(IntegrationSettingsDB).where(
            IntegrationSettingsDB.settings_id == settings_id
        )
        result = await db.execute(stmt)
        settings_db = result.scalar_one_or_none()

        if not settings_db:
            return None

        return await self._convert_to_model(settings_db, db)

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
            ValueError: If settings not found
        """
        # Get existing settings
        stmt = select(IntegrationSettingsDB).where(
            IntegrationSettingsDB.settings_id == settings_id
        )
        result = await db.execute(stmt)
        settings_db = result.scalar_one_or_none()

        if not settings_db:
            raise ValueError(f"Settings {settings_id} not found")

        # Update credentials
        if settings.credentials:
            if settings_db.credentials_id:
                await self._update_credentials(
                    settings_db.credentials_id,
                    settings.credentials,
                    db
                )
            else:
                cred_db = await self._create_credentials(settings.credentials, db)
                settings_db.credentials_id = cred_db.credential_id

        # Update clerk credentials
        if settings.clerk_credentials:
            if settings_db.clerk_credentials_id:
                await self._update_clerk_credentials(
                    settings_db.clerk_credentials_id,
                    settings.clerk_credentials,
                    db
                )
            else:
                clerk_db = await self._create_clerk_credentials(
                    settings.clerk_credentials,
                    db
                )
                settings_db.clerk_credentials_id = clerk_db.credential_id

        # Update eligibility credentials
        if settings.eligibility_credentials:
            if settings_db.eligibility_credentials_id:
                await self._update_eligibility_credentials(
                    settings_db.eligibility_credentials_id,
                    settings.eligibility_credentials,
                    db
                )
            else:
                elig_db = await self._create_eligibility_credentials(
                    settings.eligibility_credentials,
                    db
                )
                settings_db.eligibility_credentials_id = elig_db.credential_id

        # Update envelope credentials
        if settings.envelope_credentials:
            if settings_db.envelope_credentials_id:
                await self._update_envelope_credentials(
                    settings_db.envelope_credentials_id,
                    settings.envelope_credentials,
                    db
                )
            else:
                env_db = await self._create_envelope_credentials(
                    settings.envelope_credentials,
                    db
                )
                settings_db.envelope_credentials_id = env_db.credential_id

        await db.commit()
        await db.refresh(settings_db)

        return await self._convert_to_model(settings_db, db)

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
        stmt = select(IntegrationSettingsDB).where(
            IntegrationSettingsDB.settings_id == settings_id
        )
        result = await db.execute(stmt)
        settings_db = result.scalar_one_or_none()

        if not settings_db:
            raise ValueError(f"Settings {settings_id} not found")

        # Delete associated credentials
        if settings_db.credentials_id:
            await self._delete_credentials(settings_db.credentials_id, db)
        if settings_db.clerk_credentials_id:
            await self._delete_clerk_credentials(settings_db.clerk_credentials_id, db)
        if settings_db.eligibility_credentials_id:
            await self._delete_eligibility_credentials(
                settings_db.eligibility_credentials_id,
                db
            )
        if settings_db.envelope_credentials_id:
            await self._delete_envelope_credentials(
                settings_db.envelope_credentials_id,
                db
            )

        await db.delete(settings_db)
        await db.commit()

    async def _convert_to_model(
        self,
        settings_db: IntegrationSettingsDB,
        db: AsyncSession
    ) -> IntegrationSettings:
        """Convert database model to Pydantic model."""
        # Implementation details for converting DB models to Pydantic models
        pass  # For brevity, actual implementation would go here
