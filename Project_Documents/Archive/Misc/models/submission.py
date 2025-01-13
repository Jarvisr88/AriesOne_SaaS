"""Submission models module."""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class VoidMethod(str, Enum):
    """Enumeration for void methods."""
    
    VOID = "void"
    REPLACEMENT = "replacement"

class Submission(Base):
    """Model for submissions."""
    
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True)
    claim_number = Column(String(100), nullable=False, unique=True)
    status = Column(String(50), nullable=False, default='active')
    void_method = Column(SQLEnum(VoidMethod), nullable=True)
    void_reason = Column(String(500))
    void_date = Column(DateTime)
    metadata = Column(JSONB)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    replacement = relationship(
        "Submission",
        uselist=False,
        remote_side=[id],
        backref="original_submission"
    )

    def __repr__(self):
        return f"<Submission(id={self.id}, claim_number={self.claim_number}, status={self.status})>"

    def void(self, method: VoidMethod, reason: str, replacement_id: Optional[int] = None):
        """Void the submission."""
        self.status = 'voided'
        self.void_method = method
        self.void_reason = reason
        self.void_date = datetime.utcnow()
        
        if method == VoidMethod.REPLACEMENT and replacement_id:
            self.replacement_id = replacement_id
