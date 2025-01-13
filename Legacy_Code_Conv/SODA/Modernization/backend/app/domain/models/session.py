"""Session model for managing user sessions."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID

from .base import Base
from .user import User

class Session(Base):
    """Session model for tracking user sessions and activity."""

    __tablename__ = "sessions"

    # Foreign key to user
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship("User", back_populates="sessions")

    # Session data
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    ip_address: Mapped[str] = mapped_column(String(45))  # IPv6 length
    user_agent: Mapped[str] = mapped_column(String(255))
    
    # Session state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    
    # Additional data
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )

    def __init__(self, **kwargs):
        """Initialize session with default values."""
        super().__init__(**kwargs)
        if not self.expires_at:
            # Default expiration to 24 hours from creation
            self.expires_at = datetime.utcnow() + timedelta(hours=24)

    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return (
            not self.is_active or
            datetime.utcnow() >= self.expires_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "token": self.token,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_active": self.is_active,
            "expires_at": self.expires_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()

    def extend(self, hours: int = 24) -> None:
        """Extend session expiration time."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)

    def invalidate(self) -> None:
        """Invalidate the session."""
        self.is_active = False
        self.expires_at = datetime.utcnow()
