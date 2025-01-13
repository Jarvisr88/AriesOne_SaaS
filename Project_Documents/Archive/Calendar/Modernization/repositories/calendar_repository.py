"""
Calendar Repository Module
Handles data persistence for calendar operations.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models.calendar_event_model import CalendarEvent
from ..database.models import CalendarEventDB

class CalendarRepository:
    """Repository for calendar event persistence."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    async def save_event(self, event: CalendarEvent, event_id: str) -> str:
        """Save event to database."""
        db_event = CalendarEventDB(
            event_id=event_id,
            calendar_id=event.calendar_id,
            summary=event.summary,
            description=event.description,
            start_time=event.start.datetime,
            end_time=event.end.datetime,
            timezone=event.start.timezone,
            reminders=event.reminders.json()
        )
        
        self.session.add(db_event)
        await self.session.commit()
        await self.session.refresh(db_event)
        
        return event_id

    async def get_event(self, event_id: str) -> Optional[CalendarEvent]:
        """Get event by ID."""
        result = await self.session.execute(
            select(CalendarEventDB).where(CalendarEventDB.event_id == event_id)
        )
        db_event = result.scalar_one_or_none()
        
        if db_event:
            return CalendarEvent(
                calendar_id=db_event.calendar_id,
                summary=db_event.summary,
                description=db_event.description,
                start=EventTime(
                    datetime=db_event.start_time,
                    timezone=db_event.timezone
                ),
                end=EventTime(
                    datetime=db_event.end_time,
                    timezone=db_event.timezone
                ),
                reminders=db_event.reminders
            )
        return None

    async def delete_event(self, event_id: str) -> bool:
        """Delete event by ID."""
        result = await self.session.execute(
            delete(CalendarEventDB).where(CalendarEventDB.event_id == event_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def list_events(
        self,
        calendar_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        """List events with optional time range filter."""
        query = select(CalendarEventDB).where(
            CalendarEventDB.calendar_id == calendar_id
        )
        
        if start_time:
            query = query.where(CalendarEventDB.start_time >= start_time)
        if end_time:
            query = query.where(CalendarEventDB.end_time <= end_time)
            
        result = await self.session.execute(query)
        db_events = result.scalars().all()
        
        return [
            CalendarEvent(
                calendar_id=event.calendar_id,
                summary=event.summary,
                description=event.description,
                start=EventTime(
                    datetime=event.start_time,
                    timezone=event.timezone
                ),
                end=EventTime(
                    datetime=event.end_time,
                    timezone=event.timezone
                ),
                reminders=event.reminders
            )
            for event in db_events
        ]
