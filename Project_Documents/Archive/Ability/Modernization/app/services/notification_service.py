from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import BackgroundTasks

from app.models.calendar import Event, EventAttendee, NotificationPreference
from app.core.config import settings
from app.services.email_service import EmailService
from app.services.push_notification_service import PushNotificationService
from app.services.sms_service import SMSService

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
        self.push_service = PushNotificationService()
        self.sms_service = SMSService()

    async def notify_calendar_share(
        self,
        calendar_id: int,
        user_id: int,
        shared_by_id: int
    ) -> None:
        """Notify user about calendar being shared with them"""
        prefs = self._get_notification_preferences(user_id, calendar_id)
        if not prefs:
            return

        calendar = self.db.query(Calendar).get(calendar_id)
        shared_by = self.db.query(User).get(shared_by_id)

        notification_data = {
            "type": "calendar_shared",
            "calendar_name": calendar.name,
            "shared_by": shared_by.full_name
        }

        await self._send_notifications(
            user_id=user_id,
            prefs=prefs,
            notification_data=notification_data
        )

    async def notify_event_created(self, event_id: int) -> None:
        """Notify attendees about new event"""
        event = self.db.query(Event).get(event_id)
        if not event:
            return

        for attendee in event.attendees:
            if attendee.user_id != event.creator_id:
                prefs = self._get_notification_preferences(
                    attendee.user_id,
                    event.calendar_id
                )
                if not prefs or not prefs.notify_for_invites:
                    continue

                notification_data = {
                    "type": "event_invitation",
                    "event_title": event.title,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "creator_name": event.creator.full_name
                }

                await self._send_notifications(
                    user_id=attendee.user_id,
                    prefs=prefs,
                    notification_data=notification_data
                )

    async def notify_event_updated(self, event_id: int) -> None:
        """Notify attendees about event updates"""
        event = self.db.query(Event).get(event_id)
        if not event:
            return

        for attendee in event.attendees:
            prefs = self._get_notification_preferences(
                attendee.user_id,
                event.calendar_id
            )
            if not prefs or not prefs.notify_for_changes:
                continue

            notification_data = {
                "type": "event_updated",
                "event_title": event.title,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "updater_name": event.creator.full_name
            }

            await self._send_notifications(
                user_id=attendee.user_id,
                prefs=prefs,
                notification_data=notification_data
            )

    async def notify_event_deleted(self, event_id: int) -> None:
        """Notify attendees about event cancellation"""
        event = self.db.query(Event).get(event_id)
        if not event:
            return

        for attendee in event.attendees:
            prefs = self._get_notification_preferences(
                attendee.user_id,
                event.calendar_id
            )
            if not prefs or not prefs.notify_for_cancellations:
                continue

            notification_data = {
                "type": "event_cancelled",
                "event_title": event.title,
                "start_time": event.start_time.isoformat(),
                "canceller_name": event.creator.full_name
            }

            await self._send_notifications(
                user_id=attendee.user_id,
                prefs=prefs,
                notification_data=notification_data
            )

    async def notify_event_response_updated(
        self,
        event_id: int,
        user_id: int,
        response: str
    ) -> None:
        """Notify event creator about attendee response update"""
        event = self.db.query(Event).get(event_id)
        if not event:
            return

        responder = self.db.query(User).get(user_id)
        prefs = self._get_notification_preferences(
            event.creator_id,
            event.calendar_id
        )
        if not prefs or not prefs.notify_for_changes:
            return

        notification_data = {
            "type": "event_response_updated",
            "event_title": event.title,
            "responder_name": responder.full_name,
            "response": response
        }

        await self._send_notifications(
            user_id=event.creator_id,
            prefs=prefs,
            notification_data=notification_data
        )

    async def send_event_reminders(self, background_tasks: BackgroundTasks) -> None:
        """Send event reminders to attendees"""
        now = datetime.now(timezone.utc)
        
        # Find all reminders that should be sent now
        reminders = self.db.query(EventReminder).join(Event).filter(
            and_(
                Event.start_time > now,
                Event.start_time <= datetime.fromtimestamp(
                    now.timestamp() + settings.REMINDER_LOOKAHEAD_MINUTES * 60,
                    timezone.utc
                )
            )
        ).all()

        for reminder in reminders:
            prefs = self._get_notification_preferences(
                reminder.user_id,
                reminder.event.calendar_id
            )
            if not prefs or not prefs.notify_for_reminders:
                continue

            notification_data = {
                "type": "event_reminder",
                "event_title": reminder.event.title,
                "start_time": reminder.event.start_time.isoformat(),
                "minutes_before": reminder.minutes_before
            }

            background_tasks.add_task(
                self._send_notifications,
                user_id=reminder.user_id,
                prefs=prefs,
                notification_data=notification_data
            )

    def _get_notification_preferences(
        self,
        user_id: int,
        calendar_id: Optional[int] = None
    ) -> Optional[NotificationPreference]:
        """Get user's notification preferences"""
        query = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        )
        if calendar_id:
            query = query.filter(
                or_(
                    NotificationPreference.calendar_id == calendar_id,
                    NotificationPreference.calendar_id.is_(None)
                )
            )
        else:
            query = query.filter(NotificationPreference.calendar_id.is_(None))

        return query.first()

    async def _send_notifications(
        self,
        user_id: int,
        prefs: NotificationPreference,
        notification_data: Dict[str, Any]
    ) -> None:
        """Send notifications through enabled channels"""
        user = self.db.query(User).get(user_id)
        if not user:
            return

        tasks = []

        if prefs.email_enabled and user.email:
            tasks.append(
                self.email_service.send_notification(
                    email=user.email,
                    data=notification_data
                )
            )

        if prefs.push_enabled and user.push_token:
            tasks.append(
                self.push_service.send_notification(
                    token=user.push_token,
                    data=notification_data
                )
            )

        if prefs.sms_enabled and user.phone:
            tasks.append(
                self.sms_service.send_notification(
                    phone=user.phone,
                    data=notification_data
                )
            )

        # Send notifications concurrently
        await asyncio.gather(*tasks)
