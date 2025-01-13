from typing import Any, Dict, List, Optional, Type, TypeVar
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, JSON, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from pydantic import BaseModel, Field, validator
from app.db.base_class import Base
from app.core.config import settings
from app.core.cache import cache_manager

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class AuditMixin:
    """Mixin for audit fields"""
    
    @declared_attr
    def created_at(cls) -> Column:
        return Column(DateTime, nullable=False, default=datetime.utcnow)

    @declared_attr
    def updated_at(cls) -> Column:
        return Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def created_by(cls) -> Column:
        return Column(String, nullable=True)

    @declared_attr
    def updated_by(cls) -> Column:
        return Column(String, nullable=True)

class VersionMixin:
    """Mixin for version control"""
    
    @declared_attr
    def version(cls) -> Column:
        return Column(Integer, nullable=False, default=1)

    @declared_attr
    def version_changes(cls) -> Column:
        return Column(JSON, nullable=True)

class CacheMixin:
    """Mixin for caching support"""
    
    @classmethod
    async def get_cached(
        cls,
        db: AsyncSession,
        id: Any,
        cache_ttl: int = settings.DEFAULT_CACHE_TTL
    ) -> Optional[ModelType]:
        """Get item from cache or database"""
        cache_key = f"{cls.__name__}:{id}"
        
        # Try cache first
        cached = await cache_manager.get(cache_key)
        if cached:
            return cls(**cached)
        
        # Get from database
        result = await db.execute(select(cls).filter(cls.id == id))
        item = result.scalar_one_or_none()
        
        if item:
            # Cache for future use
            await cache_manager.set(
                cache_key,
                item.to_dict(),
                expire=cache_ttl
            )
        
        return item

    async def invalidate_cache(self) -> None:
        """Invalidate cache for this item"""
        cache_key = f"{self.__class__.__name__}:{self.id}"
        await cache_manager.delete(cache_key)

class AuditLogMixin:
    """Mixin for audit logging"""
    
    @declared_attr
    def audit_logs(cls) -> Column:
        return Column(JSON, nullable=True, default=list)

    def log_change(
        self,
        action: str,
        user_id: str,
        changes: Dict[str, Any] = None
    ) -> None:
        """Log a change to the audit log"""
        if not hasattr(self, "audit_logs") or self.audit_logs is None:
            self.audit_logs = []
            
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "changes": changes or {},
            "version": getattr(self, "version", 1)
        }
        
        self.audit_logs.append(log_entry)

@event.listens_for(Session, "before_flush")
def before_flush(session: Session, context, instances) -> None:
    """Handle before flush events for all models"""
    for obj in session.dirty:
        if isinstance(obj, (AuditMixin, VersionMixin)):
            # Update version
            if isinstance(obj, VersionMixin):
                obj.version += 1
                
                # Track changes
                changes = {}
                for attr in obj.__mapper__.attrs:
                    if not attr.key.startswith("_"):
                        hist = attr.history
                        if hist.has_changes():
                            changes[attr.key] = {
                                "old": hist.deleted[0] if hist.deleted else None,
                                "new": hist.added[0] if hist.added else None
                            }
                obj.version_changes = changes

class BaseSchema(BaseModel):
    """Base Pydantic schema with common validators and config"""
    
    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @validator("*", pre=True)
    def empty_str_to_none(cls, v: Any) -> Any:
        if v == "":
            return None
        return v

class BaseCreateSchema(BaseSchema):
    """Base schema for create operations"""
    pass

class BaseUpdateSchema(BaseSchema):
    """Base schema for update operations"""
    pass

class BaseInDBSchema(BaseSchema):
    """Base schema for database models"""
    id: Any
    created_at: datetime
    updated_at: datetime
    version: Optional[int] = 1
    
    class Config:
        orm_mode = True

class AuditLog(BaseSchema):
    """Schema for audit log entries"""
    timestamp: datetime
    action: str
    user_id: str
    changes: Dict[str, Any] = Field(default_factory=dict)
    version: int = 1

class VersionInfo(BaseSchema):
    """Schema for version information"""
    version: int
    changes: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
    user_id: Optional[str] = None
