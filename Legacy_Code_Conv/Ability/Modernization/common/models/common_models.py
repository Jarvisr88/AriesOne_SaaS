"""
Common Models Module

This module provides Pydantic models for common functionality.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, constr

class DataCenterType(str, Enum):
    """Data center type enumeration."""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"

class LineOfBusiness(str, Enum):
    """Line of business enumeration."""
    DME = "dme"
    HME = "hme"
    PHARMACY = "pharmacy"
    HOME_HEALTH = "home_health"
    HOSPICE = "hospice"

class ApplicationName(str, Enum):
    """Application name enumeration."""
    ABILITY = "ability"
    PORTAL = "portal"
    MOBILE = "mobile"
    API = "api"

class Application(BaseModel):
    """Application configuration model."""
    app_id: str = Field(..., description="Unique application identifier")
    name: ApplicationName = Field(..., description="Application name")
    facility_state: constr(min_length=2, max_length=2) = Field(
        ..., description="Two-letter state code"
    )
    line_of_business: LineOfBusiness = Field(..., description="Line of business")
    data_center: DataCenterType = Field(..., description="Data center type")
    pptn_region: Optional[str] = Field(None, description="PPTN region code")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "app_id": "APP123",
                "name": "ability",
                "facility_state": "CA",
                "line_of_business": "dme",
                "data_center": "production",
                "pptn_region": "WEST"
            }
        }

class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field causing error")
    details: Optional[dict] = Field(default_factory=dict, description="Additional details")

class Error(BaseModel):
    """Error model."""
    error_id: UUID = Field(default_factory=UUID.uuid4, description="Unique error ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(..., description="Error source")
    severity: str = Field(..., description="Error severity")
    message: str = Field(..., description="Error message")
    details: list[ErrorDetail] = Field(
        default_factory=list,
        description="Detailed error information"
    )
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "application",
                "severity": "error",
                "message": "Invalid application configuration",
                "details": [
                    {
                        "code": "INVALID_STATE",
                        "message": "Invalid facility state code",
                        "field": "facility_state"
                    }
                ]
            }
        }

class Credential(BaseModel):
    """Base credential model."""
    credential_id: UUID = Field(default_factory=UUID.uuid4, description="Unique credential ID")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Encrypted password")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "user123",
                "password": "encrypted_password",
                "expires_at": "2025-12-31T23:59:59Z"
            }
        }
