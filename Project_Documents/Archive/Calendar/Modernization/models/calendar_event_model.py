"""
Calendar Event Model Module
Defines Pydantic models for calendar event management.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime, timedelta

class ReminderConfig(BaseModel):
    """Configuration for event reminders."""
    method: str = Field(..., description="Reminder method (email, popup, sms)")
    minutes: int = Field(15, ge=1, le=40320, description="Minutes before event")

    @validator('method')
    def validate_method(cls, v):
        valid_methods = {'email', 'popup', 'sms'}
        if v not in valid_methods:
            raise ValueError(f'Method must be one of {valid_methods}')
        return v

class EventTime(BaseModel):
    """Event timing information."""
    datetime: datetime = Field(..., description="Event date and time")
    timezone: str = Field('UTC', description="Event timezone")

class CalendarEvent(BaseModel):
    """Calendar event details."""
    calendar_id: str = Field(..., description="Target calendar ID")
    summary: str = Field(..., min_length=1, max_length=500, description="Event summary")
    description: Optional[str] = Field(None, max_length=5000, description="Event description")
    start: EventTime
    end: Optional[EventTime] = None
    duration_minutes: int = Field(60, ge=1, le=1440, description="Event duration in minutes")
    reminders: List[ReminderConfig] = Field(
        default_factory=lambda: [
            ReminderConfig(method='email', minutes=15),
            ReminderConfig(method='popup', minutes=15),
            ReminderConfig(method='sms', minutes=15)
        ]
    )

    @validator('end', always=True)
    def set_end_time(cls, v, values):
        if v is None and 'start' in values and 'duration_minutes' in values:
            return EventTime(
                datetime=values['start'].datetime + timedelta(minutes=values['duration_minutes']),
                timezone=values['start'].timezone
            )
        return v

class CalendarList(BaseModel):
    """List of available calendars."""
    calendars: List[dict] = Field(..., description="List of calendar information")

class EventResponse(BaseModel):
    """Response after event creation."""
    event_id: str = Field(..., description="Created event ID")
    status: str = Field(..., description="Event creation status")
    html_link: Optional[str] = Field(None, description="Event URL in Google Calendar")
