"""
Calendar Database Models Module
Defines SQLAlchemy models for calendar data persistence.
"""
from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CalendarEventDB(Base):
    """Database model for calendar events."""
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    calendar_id = Column(String(100), index=True, nullable=False)
    summary = Column(String(500), nullable=False)
    description = Column(String(5000), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String(50), nullable=False, default='UTC')
    reminders = Column(JSON, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    class Config:
        """SQLAlchemy model configuration."""
        orm_mode = True
