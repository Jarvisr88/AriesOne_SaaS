"""Service for handling recurring event patterns."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from dateutil.relativedelta import relativedelta
from dateutil.rrule import (
    DAILY,
    HOURLY,
    MONTHLY,
    WEEKLY,
    YEARLY,
    rrule,
    weekday
)
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.calendar_models import (
    Event,
    EventCreate,
    EventResponse,
    EventStatus,
    RecurrenceFrequency,
    RecurrenceRule,
    WeekDay
)


class RecurrenceService:
    """Service for managing recurring events."""
    
    WEEKDAY_MAP = {
        WeekDay.MONDAY: weekday(0),
        WeekDay.TUESDAY: weekday(1),
        WeekDay.WEDNESDAY: weekday(2),
        WeekDay.THURSDAY: weekday(3),
        WeekDay.FRIDAY: weekday(4),
        WeekDay.SATURDAY: weekday(5),
        WeekDay.SUNDAY: weekday(6)
    }
    
    FREQ_MAP = {
        RecurrenceFrequency.DAILY: DAILY,
        RecurrenceFrequency.WEEKLY: WEEKLY,
        RecurrenceFrequency.MONTHLY: MONTHLY,
        RecurrenceFrequency.YEARLY: YEARLY
    }
    
    def __init__(self, session: AsyncSession):
        """Initialize recurrence service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def expand_recurring_event(
        self,
        event: Event,
        start_time: datetime,
        end_time: datetime
    ) -> List[Event]:
        """Expand recurring event into individual instances.
        
        Args:
            event: Base event
            start_time: Start of range
            end_time: End of range
            
        Returns:
            List of event instances
            
        Raises:
            HTTPException: If recurrence rule is invalid
        """
        if not event.recurrence_rule:
            return [event]
        
        try:
            # Convert recurrence rule to dateutil rrule
            rule = self._create_rrule(
                event.recurrence_rule,
                event.start_time
            )
            
            # Get all occurrence dates
            dates = rule.between(
                start_time,
                end_time,
                inc=True
            )
            
            # Create event instances
            instances = []
            event_duration = event.end_time - event.start_time
            
            for date in dates:
                instance = Event(
                    calendar_id=event.calendar_id,
                    title=event.title,
                    description=event.description,
                    location=event.location,
                    start_time=date,
                    end_time=date + event_duration,
                    timezone=event.timezone,
                    is_all_day=event.is_all_day,
                    status=event.status,
                    recurrence_id=event.id,
                    original_start_time=event.start_time,
                    color=event.color,
                    visibility=event.visibility,
                    busy_status=event.busy_status,
                    attachments=event.attachments,
                    reminders=event.reminders,
                    conference_data=event.conference_data,
                    metadata=event.metadata
                )
                instances.append(instance)
            
            return instances
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid recurrence rule: {str(e)}"
            )
    
    async def get_recurring_instances(
        self,
        event_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> List[EventResponse]:
        """Get instances of a recurring event.
        
        Args:
            event_id: Event ID
            start_time: Start of range
            end_time: End of range
            
        Returns:
            List of event instances
            
        Raises:
            HTTPException: If event not found
        """
        # Get base event
        query = select(Event).where(Event.id == event_id)
        result = await self.session.execute(query)
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )
        
        if not event.recurrence_rule:
            return [EventResponse.from_orm(event)]
        
        # Get exceptions
        exceptions = await self._get_exceptions(event_id)
        
        # Expand recurring event
        instances = await self.expand_recurring_event(
            event,
            start_time,
            end_time
        )
        
        # Apply exceptions
        final_instances = []
        for instance in instances:
            instance_start = instance.start_time
            
            # Skip if cancelled
            if instance_start in exceptions:
                continue
            
            # Check if modified
            modified = await self._get_modified_instance(
                event_id,
                instance_start
            )
            if modified:
                final_instances.append(modified)
            else:
                final_instances.append(instance)
        
        return [
            EventResponse.from_orm(instance)
            for instance in final_instances
        ]
    
    async def create_exception(
        self,
        event_id: UUID,
        original_start_time: datetime,
        update: Optional[EventCreate] = None
    ) -> Optional[EventResponse]:
        """Create exception to recurring event.
        
        Args:
            event_id: Event ID
            original_start_time: Original start time
            update: Optional update data
            
        Returns:
            Modified event instance if update provided
            
        Raises:
            HTTPException: If event not found
        """
        # Get base event
        query = select(Event).where(Event.id == event_id)
        result = await self.session.execute(query)
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )
        
        if not event.recurrence_rule:
            raise HTTPException(
                status_code=400,
                detail="Not a recurring event"
            )
        
        if update:
            # Create modified instance
            modified = Event(
                **update.dict(exclude={'calendar_id'}),
                calendar_id=event.calendar_id,
                recurrence_id=event_id,
                original_start_time=original_start_time
            )
            self.session.add(modified)
            await self.session.commit()
            await self.session.refresh(modified)
            return EventResponse.from_orm(modified)
        else:
            # Create cancelled instance
            cancelled = Event(
                calendar_id=event.calendar_id,
                title=event.title,
                start_time=original_start_time,
                end_time=original_start_time + (
                    event.end_time - event.start_time
                ),
                timezone=event.timezone,
                status=EventStatus.CANCELLED,
                recurrence_id=event_id,
                original_start_time=original_start_time
            )
            self.session.add(cancelled)
            await self.session.commit()
            return None
    
    async def update_recurring_event(
        self,
        event_id: UUID,
        update: EventCreate,
        update_all: bool = False
    ) -> List[EventResponse]:
        """Update recurring event.
        
        Args:
            event_id: Event ID
            update: Update data
            update_all: Update all future instances
            
        Returns:
            List of updated events
            
        Raises:
            HTTPException: If event not found
        """
        # Get base event
        query = select(Event).where(Event.id == event_id)
        result = await self.session.execute(query)
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )
        
        if not event.recurrence_rule:
            raise HTTPException(
                status_code=400,
                detail="Not a recurring event"
            )
        
        if update_all:
            # Update base event
            for field, value in update.dict(
                exclude={'calendar_id'}
            ).items():
                setattr(event, field, value)
            
            # Delete future exceptions
            await self._delete_future_exceptions(
                event_id,
                event.start_time
            )
            
            await self.session.commit()
            await self.session.refresh(event)
            
            return [EventResponse.from_orm(event)]
        else:
            # Create single exception
            modified = await self.create_exception(
                event_id,
                event.start_time,
                update
            )
            return [modified] if modified else []
    
    def _create_rrule(
        self,
        rule: RecurrenceRule,
        start_time: datetime
    ) -> rrule:
        """Create dateutil rrule from recurrence rule.
        
        Args:
            rule: Recurrence rule
            start_time: Start time
            
        Returns:
            dateutil rrule
        """
        kwargs = {
            "freq": self.FREQ_MAP[rule.frequency],
            "interval": rule.interval,
            "dtstart": start_time
        }
        
        if rule.count:
            kwargs["count"] = rule.count
        
        if rule.until:
            kwargs["until"] = rule.until
        
        if rule.by_day:
            kwargs["byweekday"] = [
                self.WEEKDAY_MAP[day]
                for day in rule.by_day
            ]
        
        if rule.by_month_day:
            kwargs["bymonthday"] = rule.by_month_day
        
        if rule.by_month:
            kwargs["bymonth"] = rule.by_month
        
        if rule.by_year_day:
            kwargs["byyearday"] = rule.by_year_day
        
        if rule.by_week_no:
            kwargs["byweekno"] = rule.by_week_no
        
        if rule.by_hour:
            kwargs["byhour"] = rule.by_hour
        
        if rule.by_minute:
            kwargs["byminute"] = rule.by_minute
        
        if rule.by_second:
            kwargs["bysecond"] = rule.by_second
        
        kwargs["wkst"] = self.WEEKDAY_MAP[rule.week_start]
        
        return rrule(**kwargs)
    
    async def _get_exceptions(
        self,
        event_id: UUID
    ) -> Set[datetime]:
        """Get cancelled instances of event.
        
        Args:
            event_id: Event ID
            
        Returns:
            Set of cancelled instance start times
        """
        query = select(Event).where(
            and_(
                Event.recurrence_id == event_id,
                Event.status == EventStatus.CANCELLED
            )
        )
        result = await self.session.execute(query)
        exceptions = result.scalars().all()
        
        return {
            exception.original_start_time
            for exception in exceptions
        }
    
    async def _get_modified_instance(
        self,
        event_id: UUID,
        start_time: datetime
    ) -> Optional[Event]:
        """Get modified instance of event.
        
        Args:
            event_id: Event ID
            start_time: Instance start time
            
        Returns:
            Modified event instance if exists
        """
        query = select(Event).where(
            and_(
                Event.recurrence_id == event_id,
                Event.original_start_time == start_time,
                Event.status != EventStatus.CANCELLED
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def _delete_future_exceptions(
        self,
        event_id: UUID,
        start_time: datetime
    ) -> None:
        """Delete future exceptions of event.
        
        Args:
            event_id: Event ID
            start_time: Start time
        """
        query = select(Event).where(
            and_(
                Event.recurrence_id == event_id,
                Event.original_start_time >= start_time
            )
        )
        result = await self.session.execute(query)
        exceptions = result.scalars().all()
        
        for exception in exceptions:
            await self.session.delete(exception)
