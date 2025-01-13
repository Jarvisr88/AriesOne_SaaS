"""Credentials models module."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, SecretStr, validator
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from cryptography.fernet import Fernet

from .base import Base
from ..utils.encryption import encrypt_value, decrypt_value

class CredentialType(str, Enum):
    """Credential type enumeration."""
    
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    SSH_KEY = "ssh_key"
    OTHER = "other"

class CredentialStatus(str, Enum):
    """Credential status enumeration."""
    
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ROTATED = "rotated"

class Credential(Base):
    """Credential model for secure storage."""
    
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    type = Column(SQLEnum(CredentialType), nullable=False)
    status = Column(SQLEnum(CredentialStatus), nullable=False, default=CredentialStatus.ACTIVE)
    encrypted_value = Column(String, nullable=False)
    metadata = Column(JSONB, default={})
    expires_at = Column(DateTime)
    last_rotated = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="credentials")
    audit_logs = relationship("CredentialAuditLog", back_populates="credential")

    def set_value(self, value: str, encryption_key: bytes) -> None:
        """Encrypt and set credential value."""
        self.encrypted_value = encrypt_value(value, encryption_key)

    def get_value(self, encryption_key: bytes) -> str:
        """Decrypt and return credential value."""
        return decrypt_value(self.encrypted_value, encryption_key)

class CredentialAuditLog(Base):
    """Audit log for credential operations."""
    
    __tablename__ = "credential_audit_logs"

    id = Column(Integer, primary_key=True)
    credential_id = Column(Integer, ForeignKey("credentials.id"))
    action = Column(String(50), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"))
    details = Column(JSONB, default={})
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    credential = relationship("Credential", back_populates="audit_logs")
    actor = relationship("User")

# Pydantic models for API
class CredentialCreate(BaseModel):
    """Credential creation model with validation."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: CredentialType
    value: SecretStr
    metadata: Dict[str, Any] = Field(default_factory=dict)
    expires_at: Optional[datetime] = None

    @validator("metadata")
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata structure."""
        # Ensure metadata doesn't contain sensitive information
        sensitive_keys = {"password", "secret", "key", "token"}
        if any(key.lower() in sensitive_keys for key in v.keys()):
            raise ValueError("Metadata cannot contain sensitive information")
        return v

class CredentialResponse(BaseModel):
    """Credential response model."""
    
    id: int
    name: str
    description: Optional[str]
    type: CredentialType
    status: CredentialStatus
    metadata: Dict[str, Any]
    expires_at: Optional[datetime]
    last_rotated: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        
        orm_mode = True

class CredentialRotate(BaseModel):
    """Credential rotation model."""
    
    new_value: SecretStr
    reason: Optional[str] = Field(None, max_length=500)

class CredentialRevoke(BaseModel):
    """Credential revocation model."""
    
    reason: str = Field(..., min_length=1, max_length=500)

class AuditLogResponse(BaseModel):
    """Audit log response model."""
    
    id: int
    action: str
    actor_id: int
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        """Pydantic config."""
        
        orm_mode = True
