from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from ..models.calendar_event import CalendarEvent
from ..services.google_calendar import GoogleCalendarService

router = APIRouter(prefix="/calendar", tags=["calendar"])

async def get_calendar_service():
    """Dependency to get initialized calendar service"""
    service = GoogleCalendarService()
    await service.initialize()
    return service

@router.get("/calendars")
async def list_calendars(
    show_hidden: bool = False,
    service: GoogleCalendarService = Depends(get_calendar_service)
) -> List[dict]:
    """
    List available calendars
    
    Parameters:
        show_hidden: Whether to show hidden calendars
        service: Google Calendar service instance
        
    Returns:
        List of calendar information
    """
    try:
        return await service.list_calendars(show_hidden)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events")
async def create_event(
    event: CalendarEvent,
    service: GoogleCalendarService = Depends(get_calendar_service)
) -> dict:
    """
    Create a new calendar event
    
    Parameters:
        event: Calendar event details
        service: Google Calendar service instance
        
    Returns:
        Created event details
    """
    try:
        result = await service.create_event(event)
        return JSONResponse(
            status_code=201,
            content={"message": "Event created successfully", "event": result}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
