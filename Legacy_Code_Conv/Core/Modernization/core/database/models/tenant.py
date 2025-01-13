"""
Core Tenant Model Module
Version: 1.0.0
Last Updated: 2025-01-10
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class Tenant(Base):
    """Tenant model for multi-tenancy support."""
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    # Contact Information
    contact_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Subscription Information
    subscription_plan: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'free'")
    )
    subscription_start: Mapped[Optional[datetime]] = mapped_column(
        nullable=True
    )
    subscription_end: Mapped[Optional[datetime]] = mapped_column(
        nullable=True
    )
    
    # Settings and Configuration
    settings: Mapped[dict] = mapped_column(
        nullable=False,
        server_default=text("'{}'::jsonb")
    )
    theme: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        server_default=text("'default'")
    )
    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'UTC'")
    )
    
    # Limits and Usage
    max_users: Mapped[int] = mapped_column(
        nullable=False,
        server_default=text("10")
    )
    max_storage: Mapped[int] = mapped_column(
        nullable=False,
        server_default=text("1073741824")  # 1GB in bytes
    )
    used_storage: Mapped[int] = mapped_column(
        nullable=False,
        server_default=text("0")
    )
    
    # Relationships
    users = relationship("User", back_populates="tenant", lazy="selectin")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Tenant {self.name}>"
