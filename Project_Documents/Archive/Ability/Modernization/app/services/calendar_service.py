from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException

from app.models.calendar import Calendar, Event, CalendarShare, EventAttendee, EventReminder, NotificationPreference
from app.schemas.calendar import CalendarCreate, CalendarUpdate, EventCreate, EventUpdate
from app.core.security import get_password_hash
from app.services.notification_service import NotificationService

class CalendarService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def create_calendar(
        self,
        calendar_data: CalendarCreate,
        owner_id: int,
        company_id: int
    ) -> Calendar:
        """Create a new calendar"""
        # Check if primary calendar exists for user
        if calendar_data.is_primary:
            existing_primary = self.db.query(Calendar).filter(
                Calendar.owner_id == owner_id,
                Calendar.is_primary == True
            ).first()
            if existing_primary:
                raise HTTPException(
                    status_code=400,
                    detail="User already has a primary calendar"
                )

        calendar = Calendar(
            **calendar_data.dict(),
            owner_id=owner_id,
            company_id=company_id
        )
        self.db.add(calendar)
        self.db.commit()
        self.db.refresh(calendar)
        return calendar

    def get_calendar(
        self,
        calendar_id: int,
        user_id: int,
        company_id: int
    ) -> Optional[Calendar]:
        """Get calendar by ID"""
        return self.db.query(Calendar).filter(
            Calendar.id == calendar_id,
            Calendar.company_id == company_id,
            or_(
                Calendar.owner_id == user_id,
                Calendar.shares.any(CalendarShare.user_id == user_id)
            )
        ).first()

    def list_calendars(
        self,
        user_id: int,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Calendar]:
        """List calendars for user"""
        return self.db.query(Calendar).filter(
            Calendar.company_id == company_id,
            or_(
                Calendar.owner_id == user_id,
                Calendar.shares.any(CalendarShare.user_id == user_id)
            )
        ).offset(skip).limit(limit).all()

    def update_calendar(
        self,
        calendar_id: int,
        calendar_data: CalendarUpdate,
        user_id: int,
        company_id: int
    ) -> Optional[Calendar]:
        """Update calendar"""
        calendar = self.get_calendar(calendar_id, user_id, company_id)
        if not calendar:
            return None

        # Check permissions
        if calendar.owner_id != user_id:
            share = next(
                (s for s in calendar.shares if s.user_id == user_id),
                None
            )
            if not share or share.permission != "admin":
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )

        for key, value in calendar_data.dict(exclude_unset=True).items():
            setattr(calendar, key, value)

        self.db.commit()
        self.db.refresh(calendar)
        return calendar

    def delete_calendar(
        self,
        calendar_id: int,
        user_id: int,
        company_id: int
    ) -> bool:
        """Delete calendar"""
        calendar = self.get_calendar(calendar_id, user_id, company_id)
        if not calendar:
            return False

        if calendar.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Only calendar owner can delete calendar"
            )

        if calendar.is_primary:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete primary calendar"
            )

        self.db.delete(calendar)
        self.db.commit()
        return True

    def share_calendar(
        self,
        calendar_id: int,
        user_id: int,
        target_user_id: int,
        permission: str,
        company_id: int
    ) -> CalendarShare:
        """Share calendar with another user"""
        calendar = self.get_calendar(calendar_id, user_id, company_id)
        if not calendar:
            raise HTTPException(
                status_code=404,
                detail="Calendar not found"
            )

        if calendar.owner_id != user_id:
            share = next(
                (s for s in calendar.shares if s.user_id == user_id),
                None
            )
            if not share or share.permission != "admin":
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )

        # Check if share already exists
        existing_share = next(
            (s for s in calendar.shares if s.user_id == target_user_id),
            None
        )
        if existing_share:
            existing_share.permission = permission
            self.db.commit()
            self.db.refresh(existing_share)
            return existing_share

        # Create new share
        share = CalendarShare(
            calendar_id=calendar_id,
            user_id=target_user_id,
            permission=permission
        )
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)

        # Send notification
        self.notification_service.notify_calendar_share(
            calendar_id=calendar_id,
            user_id=target_user_id,
            shared_by_id=user_id
        )

        return share

    def create_event(
        self,
        event_data: EventCreate,
        calendar_id: int,
        creator_id: int,
        company_id: int
    ) -> Event:
        """Create a new event"""
        calendar = self.get_calendar(calendar_id, creator_id, company_id)
        if not calendar:
            raise HTTPException(
                status_code=404,
                detail="Calendar not found"
            )

        # Check write permission
        if calendar.owner_id != creator_id:
            share = next(
                (s for s in calendar.shares if s.user_id == creator_id),
                None
            )
            if not share or share.permission not in ["write", "admin"]:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )

        event = Event(
            **event_data.dict(),
            calendar_id=calendar_id,
            creator_id=creator_id,
            company_id=company_id
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        # Add creator as attendee
        attendee = EventAttendee(
            event_id=event.id,
            user_id=creator_id,
            response_status="accepted"
        )
        self.db.add(attendee)

        # Add other attendees
        if event_data.attendees:
            for user_id in event_data.attendees:
                if user_id != creator_id:
                    attendee = EventAttendee(
                        event_id=event.id,
                        user_id=user_id
                    )
                    self.db.add(attendee)

        # Add reminders
        if event_data.reminders:
            for reminder_data in event_data.reminders:
                reminder = EventReminder(
                    event_id=event.id,
                    user_id=creator_id,
                    **reminder_data.dict()
                )
                self.db.add(reminder)

        self.db.commit()

        # Send notifications
        self.notification_service.notify_event_created(event.id)

        return event

    def get_event(
        self,
        event_id: int,
        user_id: int,
        company_id: int
    ) -> Optional[Event]:
        """Get event by ID"""
        return self.db.query(Event).filter(
            Event.id == event_id,
            Event.company_id == company_id,
            or_(
                Event.calendar.has(Calendar.owner_id == user_id),
                Event.calendar.has(
                    Calendar.shares.any(CalendarShare.user_id == user_id)
                ),
                Event.attendees.any(EventAttendee.user_id == user_id)
            )
        ).first()

    def list_events(
        self,
        calendar_id: int,
        user_id: int,
        company_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """List events for calendar"""
        query = self.db.query(Event).filter(
            Event.calendar_id == calendar_id,
            Event.company_id == company_id
        )

        if start_time:
            query = query.filter(Event.end_time >= start_time)
        if end_time:
            query = query.filter(Event.start_time <= end_time)

        return query.offset(skip).limit(limit).all()

    def update_event(
        self,
        event_id: int,
        event_data: EventUpdate,
        user_id: int,
        company_id: int
    ) -> Optional[Event]:
        """Update event"""
        event = self.get_event(event_id, user_id, company_id)
        if not event:
            return None

        # Check permissions
        calendar = event.calendar
        if calendar.owner_id != user_id and event.creator_id != user_id:
            share = next(
                (s for s in calendar.shares if s.user_id == user_id),
                None
            )
            if not share or share.permission not in ["write", "admin"]:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )

        # Update event fields
        for key, value in event_data.dict(exclude_unset=True).items():
            if key not in ["attendees", "reminders"]:
                setattr(event, key, value)

        # Update attendees if provided
        if event_data.attendees is not None:
            current_attendees = {a.user_id: a for a in event.attendees}
            new_attendees = set(event_data.attendees)

            # Remove attendees not in new list
            for user_id, attendee in current_attendees.items():
                if user_id not in new_attendees:
                    self.db.delete(attendee)

            # Add new attendees
            for user_id in new_attendees:
                if user_id not in current_attendees:
                    attendee = EventAttendee(
                        event_id=event.id,
                        user_id=user_id
                    )
                    self.db.add(attendee)

        # Update reminders if provided
        if event_data.reminders is not None:
            # Remove existing reminders
            for reminder in event.reminders:
                self.db.delete(reminder)

            # Add new reminders
            for reminder_data in event_data.reminders:
                reminder = EventReminder(
                    event_id=event.id,
                    user_id=user_id,
                    **reminder_data.dict()
                )
                self.db.add(reminder)

        self.db.commit()
        self.db.refresh(event)

        # Send notifications
        self.notification_service.notify_event_updated(event.id)

        return event

    def delete_event(
        self,
        event_id: int,
        user_id: int,
        company_id: int
    ) -> bool:
        """Delete event"""
        event = self.get_event(event_id, user_id, company_id)
        if not event:
            return False

        # Check permissions
        calendar = event.calendar
        if calendar.owner_id != user_id and event.creator_id != user_id:
            share = next(
                (s for s in calendar.shares if s.user_id == user_id),
                None
            )
            if not share or share.permission not in ["write", "admin"]:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )

        # Send notifications before deletion
        self.notification_service.notify_event_deleted(event.id)

        self.db.delete(event)
        self.db.commit()
        return True

    def update_event_response(
        self,
        event_id: int,
        user_id: int,
        response: str,
        company_id: int
    ) -> Optional[EventAttendee]:
        """Update attendee response to event"""
        event = self.get_event(event_id, user_id, company_id)
        if not event:
            return None

        attendee = next(
            (a for a in event.attendees if a.user_id == user_id),
            None
        )
        if not attendee:
            raise HTTPException(
                status_code=404,
                detail="User is not an attendee of this event"
            )

        attendee.response_status = response
        self.db.commit()
        self.db.refresh(attendee)

        # Send notifications
        self.notification_service.notify_event_response_updated(
            event_id=event_id,
            user_id=user_id,
            response=response
        )

        return attendee
