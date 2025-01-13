from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from app.db.base_class import Base
from app.models.user import User

class CalendarType(str, enum.Enum):
    PERSONAL = "personal"
    SHARED = "shared"
    RESOURCE = "resource"
    COMPANY = "company"

class Calendar(Base):
    __tablename__ = "calendars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(Enum(CalendarType), nullable=False, default=CalendarType.PERSONAL)
    timezone = Column(String, nullable=False, default="UTC")
    color = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)
    settings = Column(JSONB, nullable=False, default=dict)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    owner = relationship("User", back_populates="calendars")
    events = relationship("Event", back_populates="calendar", cascade="all, delete-orphan")
    shares = relationship("CalendarShare", back_populates="calendar", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    all_day = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)  # iCal RRULE format
    recurrence_exception_dates = Column(JSONB, nullable=True)  # List of excluded dates
    status = Column(String, nullable=False, default="confirmed")
    color = Column(String, nullable=True)
    settings = Column(JSONB, nullable=False, default=dict)
    
    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    calendar = relationship("Calendar", back_populates="events")
    creator = relationship("User")
    attendees = relationship("EventAttendee", back_populates="event", cascade="all, delete-orphan")
    reminders = relationship("EventReminder", back_populates="event", cascade="all, delete-orphan")

class CalendarShare(Base):
    __tablename__ = "calendar_shares"

    id = Column(Integer, primary_key=True, index=True)
    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission = Column(String, nullable=False, default="read")  # read, write, admin
    settings = Column(JSONB, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    calendar = relationship("Calendar", back_populates="shares")
    user = relationship("User")

class EventAttendee(Base):
    __tablename__ = "event_attendees"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    response_status = Column(String, nullable=False, default="pending")  # pending, accepted, declined, tentative
    settings = Column(JSONB, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    event = relationship("Event", back_populates="attendees")
    user = relationship("User")

class EventReminder(Base):
    __tablename__ = "event_reminders"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reminder_type = Column(String, nullable=False)  # email, notification, sms
    minutes_before = Column(Integer, nullable=False)
    settings = Column(JSONB, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    event = relationship("Event", back_populates="reminders")
    user = relationship("User")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=True)
    
    # Notification channels
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    
    # Event types to notify for
    notify_for_invites = Column(Boolean, default=True)
    notify_for_changes = Column(Boolean, default=True)
    notify_for_cancellations = Column(Boolean, default=True)
    notify_for_reminders = Column(Boolean, default=True)
    
    settings = Column(JSONB, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User")
    calendar = relationship("Calendar")
