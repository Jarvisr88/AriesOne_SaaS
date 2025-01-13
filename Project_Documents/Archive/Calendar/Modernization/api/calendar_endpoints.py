"""
Calendar API Endpoints Module
Provides FastAPI routes for calendar operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import List
from ..models.calendar_event_model import CalendarEvent, CalendarList, EventResponse
from ..services.calendar_service import CalendarService
from ..security.oauth_handler import get_current_user

router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

@router.get("/calendars", response_model=CalendarList)
async def get_calendars(
    current_user = Security(get_current_user),
    service: CalendarService = Depends()
):
    """Get list of available calendars."""
    try:
        return await service.list_calendars(current_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events", response_model=EventResponse)
async def create_event(
    event: CalendarEvent,
    current_user = Security(get_current_user),
    service: CalendarService = Depends()
):
    """Create a new calendar event."""
    try:
        return await service.create_event(current_user, event)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}", response_model=CalendarEvent)
async def get_event(
    event_id: str,
    current_user = Security(get_current_user),
    service: CalendarService = Depends()
):
    """Get event details by ID."""
    try:
        return await service.get_event(current_user, event_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    current_user = Security(get_current_user),
    service: CalendarService = Depends()
):
    """Delete an event by ID."""
    try:
        await service.delete_event(current_user, event_id)
        return {"status": "success", "message": "Event deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
