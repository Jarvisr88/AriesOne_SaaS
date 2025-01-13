"""
Ability Credentials Models Module

This module provides Pydantic models for various credential types.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, SecretStr

class AbilityCredentials(BaseModel):
    """Base credentials model for Ability services."""
    credential_id: UUID = Field(default_factory=UUID.uuid4)
    sender_id: str = Field(..., description="Sender identifier")
    username: str = Field(..., description="Username")
    password: SecretStr = Field(..., description="Encrypted password")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "sender_id": "SENDER123",
                "username": "user@example.com",
                "password": "encrypted_password"
            }
        }

class EnvelopeCredentials(AbilityCredentials):
    """Credentials model for envelope services."""
    envelope_id: str = Field(..., description="Envelope identifier")
    environment: str = Field(
        default="production",
        description="Environment (production/staging)"
    )

class EligibilityCredentials(AbilityCredentials):
    """Credentials model for eligibility services."""
    facility_id: str = Field(..., description="Facility identifier")
    api_key: SecretStr = Field(..., description="API key for eligibility service")
    
class ClerkCredentials(AbilityCredentials):
    """Credentials model for clerk services."""
    clerk_id: str = Field(..., description="Clerk identifier")
    role: str = Field(..., description="Clerk role")
    permissions: list[str] = Field(default_factory=list)
