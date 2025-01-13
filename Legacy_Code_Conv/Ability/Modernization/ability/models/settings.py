"""
Integration Settings Models Module

This module provides Pydantic models for integration settings.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .credentials import (
    AbilityCredentials,
    ClerkCredentials,
    EligibilityCredentials,
    EnvelopeCredentials
)

class IntegrationSettings(BaseModel):
    """Integration settings model."""
    settings_id: UUID = Field(default_factory=UUID.uuid4)
    credentials: Optional[AbilityCredentials] = Field(
        None, description="Base credentials"
    )
    clerk_credentials: Optional[ClerkCredentials] = Field(
        None, description="Clerk service credentials"
    )
    eligibility_credentials: Optional[EligibilityCredentials] = Field(
        None, description="Eligibility service credentials"
    )
    envelope_credentials: Optional[EnvelopeCredentials] = Field(
        None, description="Envelope service credentials"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "credentials": {
                    "sender_id": "SENDER123",
                    "username": "user@example.com",
                    "password": "encrypted_password"
                },
                "clerk_credentials": {
                    "sender_id": "CLERK123",
                    "username": "clerk@example.com",
                    "password": "encrypted_password",
                    "clerk_id": "CLK123",
                    "role": "admin"
                }
            }
        }
