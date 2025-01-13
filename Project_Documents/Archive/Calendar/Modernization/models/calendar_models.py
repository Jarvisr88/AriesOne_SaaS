"""Calendar models for the modernized Calendar module."""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import UUID

from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as SQLUUID
from sqlalchemy.orm import relationship

from ....Core.Modernization.models.base import Base


class CalendarType(str, Enum):
    """Calendar types."""
    PERSONAL = "personal"
    TEAM = "team"
    RESOURCE = "resource"
    EXTERNAL = "external"


class CalendarPermission(str, Enum):
    """Calendar permission levels."""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    NONE = "none"


class EventStatus(str, Enum):
    """Event status types."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class RecurrenceFrequency(str, Enum):
    """Recurrence frequency types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class WeekDay(str, Enum):
    """Days of the week."""
    MONDAY = "MO"
    TUESDAY = "TU"
    WEDNESDAY = "WE"
    THURSDAY = "TH"
    FRIDAY = "FR"
    SATURDAY = "SA"
    SUNDAY = "SU"


# Association tables
calendar_users = Table(
    "calendar_users",
    Base.metadata,
    Column(
        "calendar_id",
        SQLUUID(as_uuid=True),
        ForeignKey("calendars.id")
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id")
    ),
    Column(
        "permission",
        SQLEnum(CalendarPermission),
        nullable=False
    )
)

event_attendees = Table(
    "event_attendees",
    Base.metadata,
    Column(
        "event_id",
        SQLUUID(as_uuid=True),
        ForeignKey("events.id")
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id")
    ),
    Column(
        "response_status",
        String(20),
        default="pending"
    )
)


class Calendar(Base):
    """Calendar model."""
    __tablename__ = "calendars"

    id = Column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(
        SQLEnum(CalendarType),
        nullable=False,
        default=CalendarType.PERSONAL
    )
    color = Column(String(7))  # Hex color code
    is_primary = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)
    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )
    timezone = Column(String(50), nullable=False)
    sync_token = Column(String(100))
    external_id = Column(String(100))
    metadata = Column(JSONB)
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

    # Relationships
    events = relationship("Event", back_populates="calendar")
    users = relationship(
        "User",
        secondary=calendar_users,
        back_populates="calendars"
    )


class Event(Base):
    """Event model."""
    __tablename__ = "events"

    id = Column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    calendar_id = Column(
        SQLUUID(as_uuid=True),
        ForeignKey("calendars.id"),
        nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String(50), nullable=False)
    is_all_day = Column(Boolean, default=False)
    status = Column(
        SQLEnum(EventStatus),
        nullable=False,
        default=EventStatus.CONFIRMED
    )
    recurrence_rule = Column(JSONB)
    recurrence_id = Column(
        SQLUUID(as_uuid=True),
        ForeignKey("events.id")
    )
    original_start_time = Column(DateTime)
    color = Column(String(7))
    visibility = Column(String(20), default="default")
    busy_status = Column(String(20), default="busy")
    attachments = Column(ARRAY(String))
    reminders = Column(JSONB)
    conference_data = Column(JSONB)
    metadata = Column(JSONB)
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

    # Relationships
    calendar = relationship("Calendar", back_populates="events")
    attendees = relationship(
        "User",
        secondary=event_attendees,
        back_populates="events"
    )


# Pydantic models for API
class CalendarBase(BaseModel):
    """Base calendar model."""
    name: str
    description: Optional[str] = None
    type: CalendarType = CalendarType.PERSONAL
    color: Optional[str] = None
    is_primary: bool = False
    is_visible: bool = True
    timezone: str
    metadata: Optional[Dict] = None

    @validator("color")
    def validate_color(cls, v):
        """Validate color hex code."""
        if v and not v.startswith("#"):
            raise ValueError("Color must be a hex code starting with #")
        return v


class CalendarCreate(CalendarBase):
    """Calendar create model."""
    company_id: int


class CalendarUpdate(CalendarBase):
    """Calendar update model."""
    pass


class CalendarResponse(CalendarBase):
    """Calendar response model."""
    id: UUID
    owner_id: int
    company_id: int
    sync_token: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True


class RecurrenceRule(BaseModel):
    """Recurrence rule model."""
    frequency: RecurrenceFrequency
    interval: int = 1
    count: Optional[int] = None
    until: Optional[datetime] = None
    by_day: Optional[List[WeekDay]] = None
    by_month_day: Optional[List[int]] = None
    by_month: Optional[List[int]] = None
    by_year_day: Optional[List[int]] = None
    by_week_no: Optional[List[int]] = None
    by_hour: Optional[List[int]] = None
    by_minute: Optional[List[int]] = None
    by_second: Optional[List[int]] = None
    week_start: WeekDay = WeekDay.MONDAY

    @validator("interval")
    def validate_interval(cls, v):
        """Validate interval."""
        if v < 1:
            raise ValueError("Interval must be positive")
        return v

    @validator("by_month_day")
    def validate_month_days(cls, v):
        """Validate month days."""
        if v:
            for day in v:
                if not -31 <= day <= 31 or day == 0:
                    raise ValueError(
                        "Month days must be between -31 and 31, excluding 0"
                    )
        return v


class EventReminder(BaseModel):
    """Event reminder model."""
    method: str = "email"
    minutes_before: int = Field(gt=0)


class ConferenceData(BaseModel):
    """Conference data model."""
    type: str
    url: str
    meeting_id: Optional[str] = None
    password: Optional[str] = None
    phone_numbers: Optional[List[str]] = None
    additional_info: Optional[Dict] = None


class EventBase(BaseModel):
    """Base event model."""
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    timezone: str
    is_all_day: bool = False
    status: EventStatus = EventStatus.CONFIRMED
    recurrence_rule: Optional[RecurrenceRule] = None
    color: Optional[str] = None
    visibility: str = "default"
    busy_status: str = "busy"
    attachments: Optional[List[str]] = None
    reminders: Optional[List[EventReminder]] = None
    conference_data: Optional[ConferenceData] = None
    metadata: Optional[Dict] = None

    @validator("end_time")
    def validate_end_time(cls, v, values):
        """Validate end time is after start time."""
        if "start_time" in values and v < values["start_time"]:
            raise ValueError("End time must be after start time")
        return v


class EventCreate(EventBase):
    """Event create model."""
    calendar_id: UUID
    attendee_ids: Optional[List[int]] = None


class EventUpdate(EventBase):
    """Event update model."""
    pass


class EventResponse(EventBase):
    """Event response model."""
    id: UUID
    calendar_id: UUID
    recurrence_id: Optional[UUID] = None
    original_start_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True


class CalendarUserPermission(BaseModel):
    """Calendar user permission model."""
    calendar_id: UUID
    user_id: int
    permission: CalendarPermission


class EventAttendeeResponse(BaseModel):
    """Event attendee response model."""
    event_id: UUID
    user_id: int
    response_status: str
