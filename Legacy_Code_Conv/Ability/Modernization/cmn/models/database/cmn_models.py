"""
CMN (Certificate of Medical Necessity) Database Models Module

This module provides SQLAlchemy models for CMN data persistence.
"""
from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....database import Base

class CmnRequestDB(Base):
    """Database model for CMN requests."""
    __tablename__ = "cmn_requests"

    request_id: Mapped[UUID] = mapped_column(primary_key=True)
    medicare_mainframe_id: Mapped[UUID] = mapped_column(ForeignKey("medicare_mainframes.mainframe_id"))
    mock_response: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    medicare_mainframe = relationship("MedicareMainframeDB", back_populates="requests")
    response = relationship("CmnResponseDB", back_populates="request", uselist=False)

class CmnResponseDB(Base):
    """Database model for CMN responses."""
    __tablename__ = "cmn_responses"

    response_id: Mapped[UUID] = mapped_column(primary_key=True)
    request_id: Mapped[UUID] = mapped_column(ForeignKey("cmn_requests.request_id"))
    total_count: Mapped[int] = mapped_column(Integer)
    returned_count: Mapped[int] = mapped_column(Integer)
    processing_time_ms: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    request = relationship("CmnRequestDB", back_populates="response")
    entries = relationship("CmnResponseEntryDB", back_populates="response")

class CmnResponseEntryDB(Base):
    """Database model for CMN response entries."""
    __tablename__ = "cmn_response_entries"

    entry_id: Mapped[UUID] = mapped_column(primary_key=True)
    response_id: Mapped[UUID] = mapped_column(ForeignKey("cmn_responses.response_id"))
    npi: Mapped[str] = mapped_column(String(10))
    hic: Mapped[str] = mapped_column(String(50), nullable=True)
    mbi: Mapped[str] = mapped_column(String(11))
    hcpcs: Mapped[str] = mapped_column(String(5))
    initial_date: Mapped[datetime] = mapped_column(DateTime)
    recert_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    length_of_need: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    response = relationship("CmnResponseDB", back_populates="entries")

class MedicareMainframeDB(Base):
    """Database model for Medicare mainframe configurations."""
    __tablename__ = "medicare_mainframes"

    mainframe_id: Mapped[UUID] = mapped_column(primary_key=True)
    carrier_id: Mapped[str] = mapped_column(String(5))
    facility_id: Mapped[str] = mapped_column(String(10))
    user_id: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(255))  # Encrypted
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    requests = relationship("CmnRequestDB", back_populates="medicare_mainframe")
