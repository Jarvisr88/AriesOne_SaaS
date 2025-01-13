from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.api import deps
from app.schemas.calendar import (
    CalendarCreate,
    CalendarUpdate,
    CalendarResponse,
    EventCreate,
    EventUpdate,
    EventResponse,
    CalendarShareCreate,
    CalendarShareResponse
)
from app.services.calendar_service import CalendarService
from app.services.rate_limiter import CompanyRateLimiter
from app.services.cache_manager import CacheManager
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/calendars", response_model=CalendarResponse)
async def create_calendar(
    calendar_data: CalendarCreate,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Create a new calendar"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = CalendarService(db)
    calendar = service.create_calendar(
        calendar_data=calendar_data,
        owner_id=current_user.id,
        company_id=current_user.company_id
    )

    # Invalidate cache
    await cache.delete_pattern(f"calendars:list:{current_user.id}:*")
    return calendar

@router.get("/calendars", response_model=List[CalendarResponse])
async def list_calendars(
    response: Response,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """List user's calendars"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    cache_key = f"calendars:list:{current_user.id}:{skip}:{limit}"
    if cached := await cache.get(cache_key):
        response.headers["X-Cache"] = "HIT"
        return cached

    service = CalendarService(db)
    calendars = service.list_calendars(
        user_id=current_user.id,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit
    )

    await cache.set(cache_key, calendars)
    response.headers["X-Cache"] = "MISS"
    return calendars

@router.get("/calendars/{calendar_id}", response_model=CalendarResponse)
async def get_calendar(
    calendar_id: int,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Get calendar by ID"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    cache_key = f"calendars:detail:{calendar_id}"
    if cached := await cache.get(cache_key):
        response.headers["X-Cache"] = "HIT"
        return cached

    service = CalendarService(db)
    calendar = service.get_calendar(
        calendar_id=calendar_id,
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")

    await cache.set(cache_key, calendar)
    response.headers["X-Cache"] = "MISS"
    return calendar

@router.put("/calendars/{calendar_id}", response_model=CalendarResponse)
async def update_calendar(
    calendar_id: int,
    calendar_data: CalendarUpdate,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Update calendar"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = CalendarService(db)
    calendar = service.update_calendar(
        calendar_id=calendar_id,
        calendar_data=calendar_data,
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")

    # Invalidate cache
    await cache.delete(f"calendars:detail:{calendar_id}")
    await cache.delete_pattern(f"calendars:list:{current_user.id}:*")
    return calendar

@router.delete("/calendars/{calendar_id}", status_code=204)
async def delete_calendar(
    calendar_id: int,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Delete calendar"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = CalendarService(db)
    if not service.delete_calendar(
        calendar_id=calendar_id,
        user_id=current_user.id,
        company_id=current_user.company_id
    ):
        raise HTTPException(status_code=404, detail="Calendar not found")

    # Invalidate cache
    await cache.delete(f"calendars:detail:{calendar_id}")
    await cache.delete_pattern(f"calendars:list:{current_user.id}:*")

@router.post("/calendars/{calendar_id}/share", response_model=CalendarShareResponse)
async def share_calendar(
    calendar_id: int,
    share_data: CalendarShareCreate,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter)
):
    """Share calendar with another user"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = CalendarService(db)
    share = service.share_calendar(
        calendar_id=calendar_id,
        user_id=current_user.id,
        target_user_id=share_data.user_id,
        permission=share_data.permission,
        company_id=current_user.company_id
    )
    return share

@router.post("/calendars/{calendar_id}/events", response_model=EventResponse)
async def create_event(
    calendar_id: int,
    event_data: EventCreate,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Create a new event"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = CalendarService(db)
    event = service.create_event(
        event_data=event_data,
        calendar_id=calendar_id,
        creator_id=current_user.id,
        company_id=current_user.company_id
    )

    # Invalidate cache
    await cache.delete_pattern(f"events:list:{calendar_id}:*")
    return event

@router.get("/calendars/{calendar_id}/events", response_model=List[EventResponse])
async def list_events(
    calendar_id: int,
    response: Response,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """List calendar events"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    cache_key = f"events:list:{calendar_id}:{start_time}:{end_time}:{skip}:{limit}"
    if cached := await cache.get(cache_key):
        response.headers["X-Cache"] = "HIT"
        return cached

    service = CalendarService(db)
    events = service.list_events(
        calendar_id=calendar_id,
        user_id=current_user.id,
        company_id=current_user.company_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )

    await cache.set(cache_key, events)
    response.headers["X-Cache"] = "MISS"
    return events

@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Get event by ID"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    cache_key = f"events:detail:{event_id}"
    if cached := await cache.get(cache_key):
        response.headers["X-Cache"] = "HIT"
        return cached

    service = CalendarService(db)
    event = service.get_event(
        event_id=event_id,
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    await cache.set(cache_key, event)
    response.headers["X-Cache"] = "MISS"
    return event

@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Update event"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = CalendarService(db)
    event = service.update_event(
        event_id=event_id,
        event_data=event_data,
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Invalidate cache
    await cache.delete(f"events:detail:{event_id}")
    await cache.delete_pattern(f"events:list:{event.calendar_id}:*")
    return event

@router.delete("/events/{event_id}", status_code=204)
async def delete_event(
    event_id: int,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Delete event"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = CalendarService(db)
    event = service.get_event(
        event_id=event_id,
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    calendar_id = event.calendar_id
    if not service.delete_event(
        event_id=event_id,
        user_id=current_user.id,
        company_id=current_user.company_id
    ):
        raise HTTPException(status_code=404, detail="Event not found")

    # Invalidate cache
    await cache.delete(f"events:detail:{event_id}")
    await cache.delete_pattern(f"events:list:{calendar_id}:*")

@router.post("/events/{event_id}/response")
async def respond_to_event(
    event_id: int,
    response_status: str = Query(..., regex="^(accepted|declined|tentative)$"),
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Respond to event invitation"""
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = CalendarService(db)
    attendee = service.update_event_response(
        event_id=event_id,
        user_id=current_user.id,
        response=response_status,
        company_id=current_user.company_id
    )
    if not attendee:
        raise HTTPException(status_code=404, detail="Event not found")

    # Invalidate cache
    await cache.delete(f"events:detail:{event_id}")
    return {"status": "success"}
