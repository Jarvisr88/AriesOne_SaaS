"""
Core Audit Model Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class AuditLog(Base):
    """Audit log for tracking system changes."""
    
    # Event Information
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    entity_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True
    )
    
    # Change Details
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    old_values: Mapped[Optional[dict]] = mapped_column(
        nullable=True
    )
    new_values: Mapped[Optional[dict]] = mapped_column(
        nullable=True
    )
    
    # Context Information
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 length
        nullable=True
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Additional Context
    correlation_id: Mapped[Optional[UUID]] = mapped_column(
        nullable=True,
        index=True
    )
    metadata: Mapped[dict] = mapped_column(
        nullable=False,
        server_default=text("'{}'::jsonb")
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<AuditLog {self.event_type} {self.entity_type}>"
