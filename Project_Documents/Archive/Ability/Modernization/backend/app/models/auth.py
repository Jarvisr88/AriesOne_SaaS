from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    status = Column(
        Enum("ACTIVE", "LOCKED", "DISABLED", name="user_status"),
        nullable=False,
        default="ACTIVE"
    )
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    biometric_data = relationship("BiometricData", back_populates="user")
    twofa = relationship("TwoFactorAuth", back_populates="user", uselist=False)
    security_audits = relationship("SecurityAudit", back_populates="user")
    auth_attempts = relationship("AuthenticationAttempt", back_populates="user")

class BiometricData(Base):
    """Biometric data model"""
    __tablename__ = "biometric_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    data_type = Column(
        Enum("FINGERPRINT", "FACE", "VOICE", name="biometric_type"),
        nullable=False
    )
    data = Column(Text, nullable=False)  # Encrypted biometric data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="biometric_data")

class TwoFactorAuth(Base):
    """Two-factor authentication model"""
    __tablename__ = "two_factor_auth"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    secret = Column(String(100), nullable=False)
    enabled = Column(Boolean, default=False)
    backup_codes = Column(JSONB)  # Encrypted backup codes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="twofa")

class SecurityAudit(Base):
    """Security audit model"""
    __tablename__ = "security_audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="security_audits")

class AuthenticationAttempt(Base):
    """Authentication attempt model"""
    __tablename__ = "authentication_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    auth_type = Column(
        Enum("PASSWORD", "BIOMETRIC", "2FA", name="auth_type"),
        nullable=False
    )
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(50))
    user_agent = Column(String(200))
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="auth_attempts")
