import pytest
from datetime import datetime, timedelta
from ....models.calendar_event import CalendarEvent, EventReminders, EventReminder

def test_calendar_event_creation():
    """Test calendar event model creation"""
    event = CalendarEvent(
        summary="Test Event",
        description="Test Description",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        calendar_id="primary"
    )
    
    assert event.summary == "Test Event"
    assert event.description == "Test Description"
    assert isinstance(event.reminders, EventReminders)
    assert len(event.reminders.overrides) == 3
    
def test_event_reminder_validation():
    """Test event reminder validation"""
    reminder = EventReminder(method="email", minutes=15)
    assert reminder.method == "email"
    assert reminder.minutes == 15
    
    with pytest.raises(ValueError):
        EventReminder(method="invalid", minutes=-1)
        
def test_event_time_validation():
    """Test event time validation"""
    start_time = datetime.now()
    end_time = start_time - timedelta(hours=1)
    
    with pytest.raises(ValueError):
        CalendarEvent(
            summary="Test Event",
            start_time=start_time,
            end_time=end_time,
            calendar_id="primary"
        )
