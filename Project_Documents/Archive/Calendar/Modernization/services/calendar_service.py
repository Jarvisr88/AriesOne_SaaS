"""
Calendar Service Module
Handles business logic for calendar operations.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from fastapi import HTTPException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.calendar_models import (
    Calendar,
    CalendarCreate,
    CalendarPermission,
    CalendarResponse,
    CalendarType,
    CalendarUpdate,
    Event,
    EventCreate,
    EventResponse,
    EventStatus,
    EventUpdate
)
from ..repositories.calendar_repository import CalendarRepository


class CalendarService:
    """Service for managing calendar operations."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(
        self,
        session: AsyncSession,
        repository: CalendarRepository
    ):
        """Initialize calendar service.
        
        Args:
            session: Database session
            repository: Calendar repository
        """
        self.session = session
        self.repository = repository

    async def create_calendar(
        self,
        calendar: CalendarCreate,
        user_id: int
    ) -> CalendarResponse:
        """Create a new calendar.
        
        Args:
            calendar: Calendar creation data
            user_id: User ID
            
        Returns:
            Created calendar
            
        Raises:
            HTTPException: If validation fails
        """
        # Check if user already has a primary calendar
        if calendar.is_primary:
            existing_primary = await self.session.execute(
                select(Calendar).where(
                    and_(
                        Calendar.owner_id == user_id,
                        Calendar.is_primary == True,
                        Calendar.company_id == calendar.company_id
                    )
                )
            )
            if existing_primary.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="User already has a primary calendar"
                )
        
        # Create calendar
        db_calendar = Calendar(
            **calendar.dict(),
            owner_id=user_id
        )
        self.session.add(db_calendar)
        await self.session.commit()
        await self.session.refresh(db_calendar)
        
        return CalendarResponse.from_orm(db_calendar)

    async def get_calendar(
        self,
        calendar_id: UUID,
        user_id: int
    ) -> Optional[CalendarResponse]:
        """Get calendar by ID.
        
        Args:
            calendar_id: Calendar ID
            user_id: User ID
            
        Returns:
            Calendar if found and accessible
            
        Raises:
            HTTPException: If calendar not found or not accessible
        """
        calendar = await self._get_calendar_with_permission(
            calendar_id,
            user_id
        )
        if not calendar:
            raise HTTPException(
                status_code=404,
                detail="Calendar not found"
            )
        
        return CalendarResponse.from_orm(calendar)

    async def update_calendar(
        self,
        calendar_id: UUID,
        calendar: CalendarUpdate,
        user_id: int
    ) -> CalendarResponse:
        """Update calendar.
        
        Args:
            calendar_id: Calendar ID
            calendar: Calendar update data
            user_id: User ID
            
        Returns:
            Updated calendar
            
        Raises:
            HTTPException: If calendar not found or not accessible
        """
        db_calendar = await self._get_calendar_with_permission(
            calendar_id,
            user_id,
            required_permission=CalendarPermission.ADMIN
        )
        if not db_calendar:
            raise HTTPException(
                status_code=404,
                detail="Calendar not found"
            )
        
        # Update fields
        for field, value in calendar.dict(exclude_unset=True).items():
            setattr(db_calendar, field, value)
        
        await self.session.commit()
        await self.session.refresh(db_calendar)
        
        return CalendarResponse.from_orm(db_calendar)

    async def delete_calendar(
        self,
        calendar_id: UUID,
        user_id: int
    ) -> None:
        """Delete calendar.
        
        Args:
            calendar_id: Calendar ID
            user_id: User ID
            
        Raises:
            HTTPException: If calendar not found or not accessible
        """
        db_calendar = await self._get_calendar_with_permission(
            calendar_id,
            user_id,
            required_permission=CalendarPermission.OWNER
        )
        if not db_calendar:
            raise HTTPException(
                status_code=404,
                detail="Calendar not found"
            )
        
        # Can't delete primary calendar
        if db_calendar.is_primary:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete primary calendar"
            )
        
        await self.session.delete(db_calendar)
        await self.session.commit()

    async def list_calendars(
        self,
        user_id: int,
        company_id: int,
        include_shared: bool = True
    ) -> List[CalendarResponse]:
        """List accessible calendars.
        
        Args:
            user_id: User ID
            company_id: Company ID
            include_shared: Include shared calendars
            
        Returns:
            List of accessible calendars
        """
        query = select(Calendar).where(
            and_(
                Calendar.company_id == company_id,
                or_(
                    Calendar.owner_id == user_id,
                    Calendar.type == CalendarType.TEAM
                )
            )
        )
        
        if include_shared:
            query = query.join(
                calendar_users,
                and_(
                    calendar_users.c.calendar_id == Calendar.id,
                    calendar_users.c.user_id == user_id
                )
            )
        
        result = await self.session.execute(query)
        calendars = result.scalars().all()
        
        return [
            CalendarResponse.from_orm(calendar)
            for calendar in calendars
        ]

    async def share_calendar(
        self,
        calendar_id: UUID,
        user_id: int,
        target_user_id: int,
        permission: CalendarPermission
    ) -> None:
        """Share calendar with user.
        
        Args:
            calendar_id: Calendar ID
            user_id: User ID (sharing the calendar)
            target_user_id: User ID to share with
            permission: Permission level
            
        Raises:
            HTTPException: If calendar not found or not accessible
        """
        db_calendar = await self._get_calendar_with_permission(
            calendar_id,
            user_id,
            required_permission=CalendarPermission.ADMIN
        )
        if not db_calendar:
            raise HTTPException(
                status_code=404,
                detail="Calendar not found"
            )
        
        # Add or update permission
        await self.session.execute(
            calendar_users.update()
            .where(
                and_(
                    calendar_users.c.calendar_id == calendar_id,
                    calendar_users.c.user_id == target_user_id
                )
            )
            .values(permission=permission)
        )
        
        await self.session.commit()

    async def create_event(
        self,
        event: EventCreate,
        user_id: int
    ) -> EventResponse:
        """Create calendar event.
        
        Args:
            event: Event creation data
            user_id: User ID
            
        Returns:
            Created event
            
        Raises:
            HTTPException: If calendar not found or not accessible
        """
        # Check calendar access
        calendar = await self._get_calendar_with_permission(
            event.calendar_id,
            user_id,
            required_permission=CalendarPermission.EDITOR
        )
        if not calendar:
            raise HTTPException(
                status_code=404,
                detail="Calendar not found"
            )
        
        # Create event
        db_event = Event(
            **event.dict(exclude={'attendee_ids'}),
            created_by=user_id
        )
        
        # Add attendees if specified
        if event.attendee_ids:
            attendees = await self._get_users(event.attendee_ids)
            db_event.attendees = attendees
        
        self.session.add(db_event)
        await self.session.commit()
        await self.session.refresh(db_event)
        
        return EventResponse.from_orm(db_event)

    async def get_event(
        self,
        event_id: UUID,
        user_id: int
    ) -> Optional[EventResponse]:
        """Get event by ID.
        
        Args:
            event_id: Event ID
            user_id: User ID
            
        Returns:
            Event if found and accessible
            
        Raises:
            HTTPException: If event not found or not accessible
        """
        event = await self._get_event_with_permission(
            event_id,
            user_id
        )
        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )
        
        return EventResponse.from_orm(event)

    async def update_event(
        self,
        event_id: UUID,
        event: EventUpdate,
        user_id: int
    ) -> EventResponse:
        """Update event.
        
        Args:
            event_id: Event ID
            event: Event update data
            user_id: User ID
            
        Returns:
            Updated event
            
        Raises:
            HTTPException: If event not found or not accessible
        """
        db_event = await self._get_event_with_permission(
            event_id,
            user_id,
            required_permission=CalendarPermission.EDITOR
        )
        if not db_event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )
        
        # Update fields
        for field, value in event.dict(exclude_unset=True).items():
            setattr(db_event, field, value)
        
        await self.session.commit()
        await self.session.refresh(db_event)
        
        return EventResponse.from_orm(db_event)

    async def delete_event(
        self,
        event_id: UUID,
        user_id: int
    ) -> None:
        """Delete event.
        
        Args:
            event_id: Event ID
            user_id: User ID
            
        Raises:
            HTTPException: If event not found or not accessible
        """
        db_event = await self._get_event_with_permission(
            event_id,
            user_id,
            required_permission=CalendarPermission.EDITOR
        )
        if not db_event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )
        
        await self.session.delete(db_event)
        await self.session.commit()

    async def list_events(
        self,
        calendar_id: UUID,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[EventStatus] = None
    ) -> List[EventResponse]:
        """List calendar events.
        
        Args:
            calendar_id: Calendar ID
            user_id: User ID
            start_time: Optional start time filter
            end_time: Optional end time filter
            status: Optional status filter
            
        Returns:
            List of events
            
        Raises:
            HTTPException: If calendar not found or not accessible
        """
        # Check calendar access
        calendar = await self._get_calendar_with_permission(
            calendar_id,
            user_id,
            required_permission=CalendarPermission.VIEWER
        )
        if not calendar:
            raise HTTPException(
                status_code=404,
                detail="Calendar not found"
            )
        
        # Build query
        query = select(Event).where(Event.calendar_id == calendar_id)
        
        if start_time:
            query = query.where(Event.end_time >= start_time)
        if end_time:
            query = query.where(Event.start_time <= end_time)
        if status:
            query = query.where(Event.status == status)
        
        result = await self.session.execute(query)
        events = result.scalars().all()
        
        return [
            EventResponse.from_orm(event)
            for event in events
        ]

    async def sync_external_calendar(
        self,
        user_credentials: Dict[str, Any],
        calendar_id: UUID
    ) -> None:
        """Sync with external calendar.
        
        Args:
            user_credentials: User's OAuth credentials
            calendar_id: Calendar ID
            
        Raises:
            HTTPException: If sync fails
        """
        try:
            service = await self.get_service(user_credentials)
            
            # Get calendar
            calendar = await self.get_calendar(
                calendar_id,
                user_credentials["user_id"]
            )
            if not calendar:
                raise HTTPException(
                    status_code=404,
                    detail="Calendar not found"
                )
            
            # Get events from external calendar
            events_result = service.events().list(
                calendarId=calendar.external_id,
                timeMin=(datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            # Process events
            for event in events_result.get('items', []):
                await self._sync_external_event(event, calendar_id)
            
        except HttpError as error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to sync calendar: {error}"
            )

    async def _get_calendar_with_permission(
        self,
        calendar_id: UUID,
        user_id: int,
        required_permission: Optional[CalendarPermission] = None
    ) -> Optional[Calendar]:
        """Get calendar with permission check.
        
        Args:
            calendar_id: Calendar ID
            user_id: User ID
            required_permission: Required permission level
            
        Returns:
            Calendar if accessible
        """
        query = select(Calendar).where(Calendar.id == calendar_id)
        result = await self.session.execute(query)
        calendar = result.scalar_one_or_none()
        
        if not calendar:
            return None
        
        # Check permissions
        if calendar.owner_id == user_id:
            return calendar
        
        if required_permission:
            query = select(calendar_users).where(
                and_(
                    calendar_users.c.calendar_id == calendar_id,
                    calendar_users.c.user_id == user_id,
                    calendar_users.c.permission >= required_permission
                )
            )
            result = await self.session.execute(query)
            if not result.scalar_one_or_none():
                return None
        
        return calendar

    async def _get_event_with_permission(
        self,
        event_id: UUID,
        user_id: int,
        required_permission: Optional[CalendarPermission] = None
    ) -> Optional[Event]:
        """Get event with permission check.
        
        Args:
            event_id: Event ID
            user_id: User ID
            required_permission: Required permission level
            
        Returns:
            Event if accessible
        """
        query = select(Event).where(Event.id == event_id)
        result = await self.session.execute(query)
        event = result.scalar_one_or_none()
        
        if not event:
            return None
        
        # Check calendar permission
        calendar = await self._get_calendar_with_permission(
            event.calendar_id,
            user_id,
            required_permission
        )
        if not calendar:
            return None
        
        return event

    async def _get_users(self, user_ids: List[int]) -> List["User"]:
        """Get users by IDs.
        
        Args:
            user_ids: List of user IDs
            
        Returns:
            List of users
        """
        query = select(User).where(User.id.in_(user_ids))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def _sync_external_event(
        self,
        external_event: Dict,
        calendar_id: UUID
    ) -> None:
        """Sync external event.
        
        Args:
            external_event: External event data
            calendar_id: Calendar ID
        """
        # Convert external event to our format
        event_data = {
            "calendar_id": calendar_id,
            "title": external_event["summary"],
            "description": external_event.get("description"),
            "location": external_event.get("location"),
            "start_time": external_event["start"].get(
                "dateTime",
                external_event["start"].get("date")
            ),
            "end_time": external_event["end"].get(
                "dateTime",
                external_event["end"].get("date")
            ),
            "timezone": external_event["start"].get("timeZone", "UTC"),
            "status": EventStatus.CONFIRMED,
            "external_id": external_event["id"]
        }
        
        # Check if event exists
        query = select(Event).where(
            Event.external_id == external_event["id"]
        )
        result = await self.session.execute(query)
        existing_event = result.scalar_one_or_none()
        
        if existing_event:
            # Update existing event
            for field, value in event_data.items():
                setattr(existing_event, field, value)
        else:
            # Create new event
            new_event = Event(**event_data)
            self.session.add(new_event)
        
        await self.session.commit()
