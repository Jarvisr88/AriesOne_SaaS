"""Audit logging module."""
from typing import Any, Dict, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infrastructure.database.base import Base

class AuditEvent(Base):
    """Audit event model."""

    __tablename__ = "audit_events"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    event_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    changes = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

class AuditEventCreate(BaseModel):
    """Audit event creation model."""

    event_type: str
    entity_type: str
    entity_id: str
    user_id: UUID
    action: str
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AuditService:
    """Service for audit logging."""

    def __init__(self, session_factory):
        """Initialize audit service.
        
        Args:
            session_factory: Database session factory.
        """
        self.session_factory = session_factory

    async def log_event(self, event: AuditEventCreate) -> None:
        """Log audit event.
        
        Args:
            event: Audit event to log.
        """
        audit_event = AuditEvent(
            timestamp=datetime.utcnow(),
            **event.dict()
        )
        
        async with self.session_factory() as session:
            session.add(audit_event)
            await session.commit()

    async def log_create(
        self,
        entity_type: str,
        entity_id: str,
        user_id: UUID,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log create event.
        
        Args:
            entity_type: Type of entity.
            entity_id: Entity ID.
            user_id: User ID.
            data: Created data.
            metadata: Optional metadata.
        """
        await self.log_event(
            AuditEventCreate(
                event_type="CREATE",
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                action="create",
                changes={"new": data},
                metadata=metadata
            )
        )

    async def log_update(
        self,
        entity_type: str,
        entity_id: str,
        user_id: UUID,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log update event.
        
        Args:
            entity_type: Type of entity.
            entity_id: Entity ID.
            user_id: User ID.
            old_data: Old data.
            new_data: New data.
            metadata: Optional metadata.
        """
        await self.log_event(
            AuditEventCreate(
                event_type="UPDATE",
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                action="update",
                changes={
                    "old": old_data,
                    "new": new_data
                },
                metadata=metadata
            )
        )

    async def log_delete(
        self,
        entity_type: str,
        entity_id: str,
        user_id: UUID,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log delete event.
        
        Args:
            entity_type: Type of entity.
            entity_id: Entity ID.
            user_id: User ID.
            data: Deleted data.
            metadata: Optional metadata.
        """
        await self.log_event(
            AuditEventCreate(
                event_type="DELETE",
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                action="delete",
                changes={"old": data},
                metadata=metadata
            )
        )
