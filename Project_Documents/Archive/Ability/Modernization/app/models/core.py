from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum

from app.db.base_class import Base

class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    ARCHIVED = "archived"

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True)
    status = Column(Enum(TenantStatus), nullable=False, default=TenantStatus.PENDING)
    subscription_tier = Column(Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE)
    settings = Column(JSONB, nullable=False, default=dict)
    features = Column(JSONB, nullable=False, default=dict)
    metadata = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    companies = relationship("Company", back_populates="tenant")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    domain = Column(String)
    settings = Column(JSONB, nullable=False, default=dict)
    features = Column(JSONB, nullable=False, default=dict)
    metadata = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="companies")
    users = relationship("User", back_populates="company")

class AuthProvider(str, enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    OKTA = "okta"
    CUSTOM = "custom"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)  # Null for SSO users
    full_name = Column(String, nullable=False)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING)
    auth_provider = Column(Enum(AuthProvider), nullable=False, default=AuthProvider.LOCAL)
    auth_provider_id = Column(String, nullable=True)  # External provider's user ID
    last_login = Column(DateTime(timezone=True), nullable=True)
    settings = Column(JSONB, nullable=False, default=dict)
    metadata = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    company = relationship("Company", back_populates="users")
    sessions = relationship("UserSession", back_populates="user")
    mfa_methods = relationship("MFAMethod", back_populates="user")

class MFAType(str, enum.Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_KEY = "hardware_key"

class MFAMethod(Base):
    __tablename__ = "mfa_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(MFAType), nullable=False)
    identifier = Column(String, nullable=False)  # Phone number, email, or key ID
    secret = Column(String, nullable=True)  # Encrypted secret for TOTP
    is_primary = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="mfa_methods")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    refresh_token = Column(String, unique=True, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String)
    user_agent = Column(String)
    device_info = Column(JSONB, nullable=True)
    is_mfa_completed = Column(Boolean, default=False)
    metadata = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class ConfigurationKey(Base):
    __tablename__ = "configuration_keys"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # Null for system-wide configs
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # Null for tenant-wide configs
    key = Column(String, nullable=False)
    value = Column(JSONB, nullable=False)
    description = Column(String)
    is_sensitive = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    metadata = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        # Ensure key uniqueness within scope (system, tenant, or company)
        sqlalchemy.UniqueConstraint('tenant_id', 'company_id', 'key', name='unique_config_key'),
    )

class AuditLogType(str, enum.Enum):
    AUTH = "auth"
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"
    SECURITY = "security"
    DATA = "data"

class CoreAuditLog(Base):
    __tablename__ = "core_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    log_type = Column(Enum(AuditLogType), nullable=False)
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)  # success, failure
    ip_address = Column(String)
    user_agent = Column(String)
    request_id = Column(String)  # For tracking related events
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)
    error_message = Column(String)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Indexes for common queries
    __table_args__ = (
        sqlalchemy.Index('idx_audit_tenant_created', 'tenant_id', 'created_at'),
        sqlalchemy.Index('idx_audit_company_created', 'company_id', 'created_at'),
        sqlalchemy.Index('idx_audit_user_created', 'user_id', 'created_at'),
    )
