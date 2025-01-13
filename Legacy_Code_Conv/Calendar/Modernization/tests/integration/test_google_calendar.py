import pytest
from datetime import datetime, timedelta
from ....services.google_calendar import GoogleCalendarService
from ....models.calendar_event import CalendarEvent

@pytest.mark.asyncio
async def test_calendar_service_initialization():
    """Test Google Calendar service initialization"""
    service = GoogleCalendarService()
    await service.initialize()
    assert service.service is not None

@pytest.mark.asyncio
async def test_list_calendars():
    """Test listing calendars"""
    service = GoogleCalendarService()
    calendars = await service.list_calendars()
    assert isinstance(calendars, list)
    for calendar in calendars:
        assert 'id' in calendar
        assert 'summary' in calendar

@pytest.mark.asyncio
async def test_create_event():
    """Test creating calendar event"""
    service = GoogleCalendarService()
    event = CalendarEvent(
        summary="Integration Test Event",
        description="Test Description",
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=1),
        calendar_id="primary"
    )
    
    result = await service.create_event(event)
    assert result.get('status') == 'confirmed'
    assert result.get('summary') == event.summary
