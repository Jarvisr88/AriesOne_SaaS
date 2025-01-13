"""Credentials API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.credentials import (
    CredentialCreate,
    CredentialResponse,
    CredentialRotate,
    CredentialRevoke,
    CredentialType,
    CredentialStatus,
    AuditLogResponse
)
from ..services.credentials_service import CredentialsService
from ..utils.encryption import KeyVaultClient
from ..database import get_async_session
from ..config import get_settings
from ..auth import get_current_user

router = APIRouter(prefix="/credentials", tags=["credentials"])

async def get_credentials_service(
    db: AsyncSession = Depends(get_async_session)
) -> CredentialsService:
    """Get credentials service instance."""
    settings = get_settings()
    key_vault = KeyVaultClient(settings.key_vault_url)
    return CredentialsService(db, key_vault)

def get_request_info(request: Request) -> dict:
    """Get request information for audit logging."""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }

@router.post("", response_model=CredentialResponse)
async def create_credential(
    credential_data: CredentialCreate,
    request: Request,
    service: CredentialsService = Depends(get_credentials_service),
    current_user = Depends(get_current_user)
):
    """Create a new credential."""
    try:
        credential = await service.create_credential(
            credential_data,
            current_user.id,
            get_request_info(request)
        )
        return credential
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=List[CredentialResponse])
async def list_credentials(
    type: Optional[CredentialType] = None,
    status: Optional[CredentialStatus] = None,
    service: CredentialsService = Depends(get_credentials_service),
    current_user = Depends(get_current_user)
):
    """List credentials with optional filters."""
    credentials = await service.list_credentials(
        current_user.id,
        type=type,
        status=status
    )
    return credentials

@router.get("/{credential_id}", response_model=CredentialResponse)
async def get_credential(
    credential_id: int,
    include_value: bool = False,
    service: CredentialsService = Depends(get_credentials_service),
    current_user = Depends(get_current_user)
):
    """Get credential by ID."""
    credential = await service.get_credential(
        credential_id,
        current_user.id,
        include_value
    )
    return credential

@router.post("/{credential_id}/rotate", response_model=CredentialResponse)
async def rotate_credential(
    credential_id: int,
    rotation_data: CredentialRotate,
    request: Request,
    service: CredentialsService = Depends(get_credentials_service),
    current_user = Depends(get_current_user)
):
    """Rotate credential value."""
    credential = await service.rotate_credential(
        credential_id,
        rotation_data.new_value.get_secret_value(),
        current_user.id,
        get_request_info(request),
        rotation_data.reason
    )
    return credential

@router.post("/{credential_id}/revoke", response_model=CredentialResponse)
async def revoke_credential(
    credential_id: int,
    revocation_data: CredentialRevoke,
    request: Request,
    service: CredentialsService = Depends(get_credentials_service),
    current_user = Depends(get_current_user)
):
    """Revoke a credential."""
    credential = await service.revoke_credential(
        credential_id,
        current_user.id,
        get_request_info(request),
        revocation_data.reason
    )
    return credential

@router.get("/{credential_id}/audit-logs", response_model=List[AuditLogResponse])
async def get_credential_audit_logs(
    credential_id: int,
    limit: int = 100,
    offset: int = 0,
    service: CredentialsService = Depends(get_credentials_service),
    current_user = Depends(get_current_user)
):
    """Get audit logs for a credential."""
    audit_logs = await service.get_audit_logs(
        credential_id,
        current_user.id,
        limit,
        offset
    )
    return audit_logs
