"""Service for handling external calendar integrations."""
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.calendar_models import (
    Calendar,
    CalendarIntegration,
    Event,
    EventCreate,
    ExternalCalendarProvider,
    ExternalCalendarSync
)


class ExternalCalendarService:
    """Service for managing external calendar integrations."""
    
    def __init__(
        self,
        session: AsyncSession,
        google_client_id: str,
        google_client_secret: str
    ):
        """Initialize external calendar service.
        
        Args:
            session: Database session
            google_client_id: Google OAuth client ID
            google_client_secret: Google OAuth client secret
        """
        self.session = session
        self.google_client_id = google_client_id
        self.google_client_secret = google_client_secret
    
    async def connect_calendar(
        self,
        user_id: UUID,
        provider: ExternalCalendarProvider,
        credentials: Dict
    ) -> CalendarIntegration:
        """Connect external calendar.
        
        Args:
            user_id: User ID
            provider: Calendar provider
            credentials: OAuth credentials
            
        Returns:
            Created calendar integration
            
        Raises:
            HTTPException: If connection fails
        """
        try:
            # Validate credentials
            if provider == ExternalCalendarProvider.GOOGLE:
                creds = Credentials(
                    token=credentials.get("access_token"),
                    refresh_token=credentials.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=self.google_client_id,
                    client_secret=self.google_client_secret
                )
                
                # Test connection
                service = build("calendar", "v3", credentials=creds)
                service.calendarList().list().execute()
            
            # Create integration record
            integration = CalendarIntegration(
                user_id=user_id,
                provider=provider,
                credentials=credentials,
                connected=True
            )
            
            self.session.add(integration)
            await self.session.commit()
            await self.session.refresh(integration)
            
            return integration
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to connect calendar: {str(e)}"
            )
    
    async def sync_calendars(
        self,
        user_id: UUID,
        integration_id: UUID
    ) -> List[Calendar]:
        """Sync external calendars.
        
        Args:
            user_id: User ID
            integration_id: Integration ID
            
        Returns:
            List of synced calendars
            
        Raises:
            HTTPException: If sync fails
        """
        try:
            # Get integration
            integration = await self._get_integration(
                integration_id,
                user_id
            )
            
            if not integration:
                raise HTTPException(
                    status_code=404,
                    detail="Integration not found"
                )
            
            if integration.provider == ExternalCalendarProvider.GOOGLE:
                return await self._sync_google_calendars(integration)
            
            return []
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to sync calendars: {str(e)}"
            )
    
    async def sync_events(
        self,
        calendar_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> List[Event]:
        """Sync external calendar events.
        
        Args:
            calendar_id: Calendar ID
            start_time: Start of sync range
            end_time: End of sync range
            
        Returns:
            List of synced events
            
        Raises:
            HTTPException: If sync fails
        """
        try:
            # Get calendar
            query = select(Calendar).where(Calendar.id == calendar_id)
            result = await self.session.execute(query)
            calendar = result.scalar_one_or_none()
            
            if not calendar or not calendar.external_id:
                raise HTTPException(
                    status_code=404,
                    detail="Calendar not found"
                )
            
            # Get integration
            integration = await self._get_integration(
                calendar.integration_id,
                calendar.user_id
            )
            
            if not integration:
                raise HTTPException(
                    status_code=404,
                    detail="Integration not found"
                )
            
            if integration.provider == ExternalCalendarProvider.GOOGLE:
                return await self._sync_google_events(
                    integration,
                    calendar,
                    start_time,
                    end_time
                )
            
            return []
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to sync events: {str(e)}"
            )
    
    async def push_event(
        self,
        event: Event
    ) -> str:
        """Push event to external calendar.
        
        Args:
            event: Event to push
            
        Returns:
            External event ID
            
        Raises:
            HTTPException: If push fails
        """
        try:
            # Get calendar
            query = select(Calendar).where(
                Calendar.id == event.calendar_id
            )
            result = await self.session.execute(query)
            calendar = result.scalar_one_or_none()
            
            if not calendar or not calendar.external_id:
                raise HTTPException(
                    status_code=404,
                    detail="Calendar not found"
                )
            
            # Get integration
            integration = await self._get_integration(
                calendar.integration_id,
                calendar.user_id
            )
            
            if not integration:
                raise HTTPException(
                    status_code=404,
                    detail="Integration not found"
                )
            
            if integration.provider == ExternalCalendarProvider.GOOGLE:
                return await self._push_google_event(
                    integration,
                    calendar,
                    event
                )
            
            return ""
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to push event: {str(e)}"
            )
    
    async def _get_integration(
        self,
        integration_id: UUID,
        user_id: UUID
    ) -> Optional[CalendarIntegration]:
        """Get calendar integration.
        
        Args:
            integration_id: Integration ID
            user_id: User ID
            
        Returns:
            Calendar integration if found
        """
        query = select(CalendarIntegration).where(
            CalendarIntegration.id == integration_id,
            CalendarIntegration.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def _sync_google_calendars(
        self,
        integration: CalendarIntegration
    ) -> List[Calendar]:
        """Sync Google calendars.
        
        Args:
            integration: Calendar integration
            
        Returns:
            List of synced calendars
            
        Raises:
            HTTPException: If sync fails
        """
        try:
            # Build service
            creds = Credentials(
                token=integration.credentials.get("access_token"),
                refresh_token=integration.credentials.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.google_client_id,
                client_secret=self.google_client_secret
            )
            
            service = build("calendar", "v3", credentials=creds)
            
            # Get calendar list
            calendars = []
            page_token = None
            
            while True:
                calendar_list = service.calendarList().list(
                    pageToken=page_token
                ).execute()
                
                for item in calendar_list["items"]:
                    calendar = Calendar(
                        user_id=integration.user_id,
                        integration_id=integration.id,
                        name=item["summary"],
                        description=item.get("description", ""),
                        color=item.get("backgroundColor", "#000000"),
                        external_id=item["id"],
                        read_only=item.get("accessRole") == "reader"
                    )
                    
                    calendars.append(calendar)
                
                page_token = calendar_list.get("nextPageToken")
                if not page_token:
                    break
            
            # Save calendars
            for calendar in calendars:
                self.session.add(calendar)
            
            await self.session.commit()
            
            return calendars
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to sync Google calendars: {str(e)}"
            )
    
    async def _sync_google_events(
        self,
        integration: CalendarIntegration,
        calendar: Calendar,
        start_time: datetime,
        end_time: datetime
    ) -> List[Event]:
        """Sync Google calendar events.
        
        Args:
            integration: Calendar integration
            calendar: Calendar
            start_time: Start of sync range
            end_time: End of sync range
            
        Returns:
            List of synced events
            
        Raises:
            HTTPException: If sync fails
        """
        try:
            # Build service
            creds = Credentials(
                token=integration.credentials.get("access_token"),
                refresh_token=integration.credentials.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.google_client_id,
                client_secret=self.google_client_secret
            )
            
            service = build("calendar", "v3", credentials=creds)
            
            # Get events
            events = []
            page_token = None
            
            while True:
                events_result = service.events().list(
                    calendarId=calendar.external_id,
                    timeMin=start_time.isoformat(),
                    timeMax=end_time.isoformat(),
                    singleEvents=True,
                    orderBy="startTime",
                    pageToken=page_token
                ).execute()
                
                for item in events_result["items"]:
                    event = await self._convert_google_event(
                        item,
                        calendar
                    )
                    events.append(event)
                
                page_token = events_result.get("nextPageToken")
                if not page_token:
                    break
            
            # Save events
            for event in events:
                self.session.add(event)
            
            await self.session.commit()
            
            return events
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to sync Google events: {str(e)}"
            )
    
    async def _push_google_event(
        self,
        integration: CalendarIntegration,
        calendar: Calendar,
        event: Event
    ) -> str:
        """Push event to Google calendar.
        
        Args:
            integration: Calendar integration
            calendar: Calendar
            event: Event to push
            
        Returns:
            Google event ID
            
        Raises:
            HTTPException: If push fails
        """
        try:
            # Build service
            creds = Credentials(
                token=integration.credentials.get("access_token"),
                refresh_token=integration.credentials.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.google_client_id,
                client_secret=self.google_client_secret
            )
            
            service = build("calendar", "v3", credentials=creds)
            
            # Convert event
            event_body = {
                "summary": event.title,
                "description": event.description,
                "start": {
                    "dateTime": event.start_time.isoformat(),
                    "timeZone": event.timezone
                },
                "end": {
                    "dateTime": event.end_time.isoformat(),
                    "timeZone": event.timezone
                }
            }
            
            if event.location:
                event_body["location"] = event.location
            
            if event.color:
                event_body["colorId"] = event.color
            
            # Create event
            result = service.events().insert(
                calendarId=calendar.external_id,
                body=event_body
            ).execute()
            
            return result["id"]
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to push Google event: {str(e)}"
            )
    
    async def _convert_google_event(
        self,
        google_event: Dict,
        calendar: Calendar
    ) -> Event:
        """Convert Google event to internal event.
        
        Args:
            google_event: Google event data
            calendar: Calendar
            
        Returns:
            Converted event
        """
        # Get start/end times
        start = google_event["start"].get(
            "dateTime",
            google_event["start"].get("date")
        )
        end = google_event["end"].get(
            "dateTime",
            google_event["end"].get("date")
        )
        
        # Convert to datetime
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        
        # Create event
        event = Event(
            calendar_id=calendar.id,
            title=google_event["summary"],
            description=google_event.get("description", ""),
            location=google_event.get("location", ""),
            start_time=start,
            end_time=end,
            timezone=google_event["start"].get("timeZone", "UTC"),
            is_all_day="date" in google_event["start"],
            color=google_event.get("colorId"),
            external_id=google_event["id"]
        )
        
        return event
