"""
AbilityCredentials API Endpoints Module
This module provides REST endpoints for credential management.
"""
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from ..models.ability_credentials_model import AbilityCredentials
from ..services.ability_credentials_service import AbilityCredentialsService
from ..security.ability_credentials_policy import CredentialsPolicy
from ..dependencies import get_credentials_service

router = APIRouter(prefix="/api/v1/credentials", tags=["credentials"])
security = HTTPBearer()

@router.post("/authenticate")
async def authenticate(
    credentials: AbilityCredentials,
    service: AbilityCredentialsService = Depends(get_credentials_service)
) -> Dict[str, Any]:
    """
    Authenticate using provided credentials.
    
    Args:
        credentials (AbilityCredentials): Credentials for authentication
        service (AbilityCredentialsService): Credentials service
        
    Returns:
        Dict[str, Any]: Authentication result
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        result = await service.authenticate(credentials)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/create")
async def create_credentials(
    credentials: AbilityCredentials,
    service: AbilityCredentialsService = Depends(get_credentials_service),
    token: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Create new credentials.
    
    Args:
        credentials (AbilityCredentials): Credentials to create
        service (AbilityCredentialsService): Credentials service
        token (HTTPAuthorizationCredentials): Authorization token
        
    Returns:
        Dict[str, Any]: Creation result
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # TODO: Verify admin token
        result = await service.create_credentials(credentials)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/security-policy")
async def get_security_policy() -> Dict[str, Any]:
    """
    Get current security policy requirements.
    
    Returns:
        Dict[str, Any]: Security policy details
    """
    return {
        "password": {
            "min_length": CredentialsPolicy.MIN_PASSWORD_LENGTH,
            "max_length": CredentialsPolicy.MAX_PASSWORD_LENGTH,
            "require_uppercase": CredentialsPolicy.REQUIRE_UPPERCASE,
            "require_lowercase": CredentialsPolicy.REQUIRE_LOWERCASE,
            "require_numbers": CredentialsPolicy.REQUIRE_NUMBERS,
            "require_special": CredentialsPolicy.REQUIRE_SPECIAL,
            "special_chars": CredentialsPolicy.SPECIAL_CHARS
        },
        "username": {
            "min_length": CredentialsPolicy.MIN_USERNAME_LENGTH,
            "max_length": CredentialsPolicy.MAX_USERNAME_LENGTH,
            "allowed_chars": CredentialsPolicy.ALLOWED_USERNAME_CHARS
        },
        "sender_id": {
            "min_length": CredentialsPolicy.MIN_SENDER_LENGTH,
            "max_length": CredentialsPolicy.MAX_SENDER_LENGTH,
            "allowed_chars": CredentialsPolicy.ALLOWED_SENDER_CHARS
        }
    }
