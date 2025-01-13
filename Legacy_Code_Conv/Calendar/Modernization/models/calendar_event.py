from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field

class EventReminder(BaseModel):
    """Model for event reminder settings"""
    method: str = Field(..., description="Reminder method (email, popup, sms)")
    minutes: int = Field(..., description="Minutes before event to send reminder")

class EventReminders(BaseModel):
    """Model for event reminders configuration"""
    use_default: bool = Field(False, alias="useDefault")
    overrides: Optional[List[EventReminder]] = None

class CalendarEvent(BaseModel):
    """Model for calendar event"""
    summary: str = Field(..., description="Event summary/title")
    description: Optional[str] = Field(None, description="Event description")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    calendar_id: str = Field(..., description="ID of the calendar")
    reminders: Optional[EventReminders] = Field(
        default_factory=lambda: EventReminders(
            use_default=False,
            overrides=[
                EventReminder(method="email", minutes=15),
                EventReminder(method="popup", minutes=15),
                EventReminder(method="sms", minutes=15)
            ]
        )
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
