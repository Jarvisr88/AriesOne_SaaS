"""Credentials service for managing secure credentials."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from ..models.credentials import (
    Credential,
    CredentialAuditLog,
    CredentialCreate,
    CredentialStatus,
    CredentialType
)
from ..utils.encryption import KeyVaultClient

class CredentialsService:
    """Service for managing credentials securely."""

    def __init__(self, db: AsyncSession, key_vault: KeyVaultClient):
        """Initialize credentials service."""
        self.db = db
        self.key_vault = key_vault

    async def create_credential(
        self,
        credential_data: CredentialCreate,
        user_id: int,
        request_info: Dict[str, str]
    ) -> Credential:
        """Create a new credential."""
        # Get encryption key
        encryption_key = await self.key_vault.get_encryption_key("credential-key")
        if not encryption_key:
            encryption_key = await self.key_vault.rotate_encryption_key("credential-key")

        # Create credential
        credential = Credential(
            name=credential_data.name,
            description=credential_data.description,
            type=credential_data.type,
            status=CredentialStatus.ACTIVE,
            metadata=credential_data.metadata,
            expires_at=credential_data.expires_at,
            created_by=user_id
        )

        # Encrypt value
        credential.set_value(credential_data.value.get_secret_value(), encryption_key)

        # Add to database
        self.db.add(credential)

        # Create audit log
        audit_log = CredentialAuditLog(
            credential=credential,
            action="create",
            actor_id=user_id,
            ip_address=request_info.get("ip_address"),
            user_agent=request_info.get("user_agent"),
            details={"type": credential_data.type}
        )
        self.db.add(audit_log)

        await self.db.commit()
        await self.db.refresh(credential)

        return credential

    async def get_credential(
        self,
        credential_id: int,
        user_id: int,
        include_value: bool = False
    ) -> Credential:
        """Get credential by ID."""
        query = (
            select(Credential)
            .options(selectinload(Credential.audit_logs))
            .filter(Credential.id == credential_id)
        )
        
        result = await self.db.execute(query)
        credential = result.scalar_one_or_none()

        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )

        if include_value:
            # Get encryption key and decrypt value
            encryption_key = await self.key_vault.get_encryption_key("credential-key")
            if encryption_key:
                credential.decrypted_value = credential.get_value(encryption_key)

        return credential

    async def list_credentials(
        self,
        user_id: int,
        type: Optional[CredentialType] = None,
        status: Optional[CredentialStatus] = None
    ) -> List[Credential]:
        """List credentials with optional filters."""
        query = select(Credential)

        if type:
            query = query.filter(Credential.type == type)
        if status:
            query = query.filter(Credential.status == status)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def rotate_credential(
        self,
        credential_id: int,
        new_value: str,
        user_id: int,
        request_info: Dict[str, str],
        reason: Optional[str] = None
    ) -> Credential:
        """Rotate credential value."""
        # Get credential
        credential = await self.get_credential(credential_id, user_id)

        # Get encryption key
        encryption_key = await self.key_vault.get_encryption_key("credential-key")
        if not encryption_key:
            encryption_key = await self.key_vault.rotate_encryption_key("credential-key")

        # Update credential
        credential.set_value(new_value, encryption_key)
        credential.status = CredentialStatus.ACTIVE
        credential.last_rotated = datetime.utcnow()

        # Create audit log
        audit_log = CredentialAuditLog(
            credential=credential,
            action="rotate",
            actor_id=user_id,
            ip_address=request_info.get("ip_address"),
            user_agent=request_info.get("user_agent"),
            details={"reason": reason} if reason else {}
        )
        self.db.add(audit_log)

        await self.db.commit()
        await self.db.refresh(credential)

        return credential

    async def revoke_credential(
        self,
        credential_id: int,
        user_id: int,
        request_info: Dict[str, str],
        reason: str
    ) -> Credential:
        """Revoke a credential."""
        # Get credential
        credential = await self.get_credential(credential_id, user_id)

        # Update status
        credential.status = CredentialStatus.REVOKED

        # Create audit log
        audit_log = CredentialAuditLog(
            credential=credential,
            action="revoke",
            actor_id=user_id,
            ip_address=request_info.get("ip_address"),
            user_agent=request_info.get("user_agent"),
            details={"reason": reason}
        )
        self.db.add(audit_log)

        await self.db.commit()
        await self.db.refresh(credential)

        return credential

    async def get_audit_logs(
        self,
        credential_id: int,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[CredentialAuditLog]:
        """Get audit logs for a credential."""
        query = (
            select(CredentialAuditLog)
            .filter(CredentialAuditLog.credential_id == credential_id)
            .order_by(CredentialAuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        return result.scalars().all()
