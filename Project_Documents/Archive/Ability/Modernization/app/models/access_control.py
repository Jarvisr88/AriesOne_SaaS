from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum

from app.db.base_class import Base

# Many-to-many relationship tables
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

group_roles = Table(
    'group_roles',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)

class ResourceType(str, enum.Enum):
    CALENDAR = "calendar"
    EVENT = "event"
    USER = "user"
    GROUP = "group"
    ROLE = "role"
    COMPANY = "company"
    REPORT = "report"
    SETTING = "setting"

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    resource_type = Column(Enum(ResourceType), nullable=False)
    action = Column(String, nullable=False)  # create, read, update, delete, etc.
    conditions = Column(JSONB, nullable=True)  # Additional conditions for permission
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    is_system_role = Column(Boolean, default=False)  # System roles cannot be modified
    parent_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    settings = Column(JSONB, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")
    groups = relationship("Group", secondary=group_roles, back_populates="roles")
    child_roles = relationship("Role", backref=relationship("Role", remote_side=[id]))

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    is_system_group = Column(Boolean, default=False)
    parent_group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    settings = Column(JSONB, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    roles = relationship("Role", secondary=group_roles, back_populates="groups")
    users = relationship("User", secondary=user_groups, back_populates="groups")
    child_groups = relationship("Group", backref=relationship("Group", remote_side=[id]))

class AccessControlList(Base):
    __tablename__ = "access_control_lists"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(Enum(ResourceType), nullable=False)
    resource_id = Column(Integer, nullable=False)
    principal_type = Column(String, nullable=False)  # user, group, role
    principal_id = Column(Integer, nullable=False)
    permissions = Column(ARRAY(String), nullable=False)  # Array of permission names
    conditions = Column(JSONB, nullable=True)  # Additional conditions
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType), nullable=False)
    resource_id = Column(Integer, nullable=False)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)  # Additional context
    ip_address = Column(String)
    user_agent = Column(String)
    status = Column(String, nullable=False)  # success, failure
    error_message = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Relationships
    actor = relationship("User")

class SecurityPolicy(Base):
    __tablename__ = "security_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    policy_type = Column(String, nullable=False)  # password, session, rate-limit, etc.
    settings = Column(JSONB, nullable=False)  # Policy-specific settings
    is_enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

# Add relationships to User model
from app.models.user import User
User.roles = relationship("Role", secondary=user_roles, back_populates="users")
User.groups = relationship("Group", secondary=user_groups, back_populates="users")
