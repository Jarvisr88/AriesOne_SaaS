"""Service for handling calendar event notifications."""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.calendar_models import (
    Event,
    EventReminder,
    NotificationChannel,
    NotificationPreference,
    NotificationStatus
)


class NotificationService:
    """Service for managing calendar event notifications."""
    
    def __init__(
        self,
        session: AsyncSession,
        background_tasks: BackgroundTasks,
        email_service: Optional[object] = None,
        sms_service: Optional[object] = None,
        push_service: Optional[object] = None
    ):
        """Initialize notification service.
        
        Args:
            session: Database session
            background_tasks: FastAPI background tasks
            email_service: Optional email service
            sms_service: Optional SMS service
            push_service: Optional push notification service
        """
        self.session = session
        self.background_tasks = background_tasks
        self.email_service = email_service
        self.sms_service = sms_service
        self.push_service = push_service
    
    async def schedule_event_notifications(
        self,
        event: Event,
        user_id: UUID
    ) -> None:
        """Schedule notifications for an event.
        
        Args:
            event: Event to schedule notifications for
            user_id: User ID
            
        Raises:
            HTTPException: If notification preferences not found
        """
        # Get user notification preferences
        prefs = await self._get_notification_preferences(user_id)
        if not prefs:
            raise HTTPException(
                status_code=404,
                detail="Notification preferences not found"
            )
        
        # Schedule reminders
        for reminder in event.reminders:
            notification_time = self._calculate_notification_time(
                event.start_time,
                reminder
            )
            
            # Skip if notification time has passed
            if notification_time <= datetime.now():
                continue
            
            # Schedule notification for each enabled channel
            for channel in prefs.channels:
                await self._create_notification(
                    event=event,
                    user_id=user_id,
                    channel=channel,
                    scheduled_time=notification_time,
                    reminder=reminder
                )
    
    async def process_due_notifications(self) -> None:
        """Process notifications that are due to be sent."""
        # Get due notifications
        query = select(NotificationStatus).where(
            and_(
                NotificationStatus.sent == False,
                NotificationStatus.scheduled_time <= datetime.now()
            )
        )
        result = await self.session.execute(query)
        notifications = result.scalars().all()
        
        # Process each notification
        for notification in notifications:
            self.background_tasks.add_task(
                self._send_notification,
                notification
            )
    
    async def cancel_event_notifications(
        self,
        event_id: UUID,
        user_id: Optional[UUID] = None
    ) -> None:
        """Cancel notifications for an event.
        
        Args:
            event_id: Event ID
            user_id: Optional user ID to cancel for specific user
        """
        # Build query
        query = select(NotificationStatus).where(
            NotificationStatus.event_id == event_id
        )
        
        if user_id:
            query = query.where(
                NotificationStatus.user_id == user_id
            )
        
        # Get notifications
        result = await self.session.execute(query)
        notifications = result.scalars().all()
        
        # Cancel each notification
        for notification in notifications:
            notification.cancelled = True
        
        await self.session.commit()
    
    async def _get_notification_preferences(
        self,
        user_id: UUID
    ) -> Optional[NotificationPreference]:
        """Get user notification preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            User notification preferences if found
        """
        query = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    def _calculate_notification_time(
        self,
        event_time: datetime,
        reminder: EventReminder
    ) -> datetime:
        """Calculate when to send notification.
        
        Args:
            event_time: Event start time
            reminder: Event reminder
            
        Returns:
            Notification time
        """
        if reminder.unit == "minutes":
            delta = timedelta(minutes=reminder.amount)
        elif reminder.unit == "hours":
            delta = timedelta(hours=reminder.amount)
        elif reminder.unit == "days":
            delta = timedelta(days=reminder.amount)
        else:
            delta = timedelta(weeks=reminder.amount)
        
        return event_time - delta
    
    async def _create_notification(
        self,
        event: Event,
        user_id: UUID,
        channel: NotificationChannel,
        scheduled_time: datetime,
        reminder: EventReminder
    ) -> NotificationStatus:
        """Create notification status record.
        
        Args:
            event: Event
            user_id: User ID
            channel: Notification channel
            scheduled_time: When to send notification
            reminder: Event reminder
            
        Returns:
            Created notification status
        """
        notification = NotificationStatus(
            event_id=event.id,
            user_id=user_id,
            channel=channel,
            scheduled_time=scheduled_time,
            reminder_amount=reminder.amount,
            reminder_unit=reminder.unit,
            sent=False,
            cancelled=False
        )
        
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        
        return notification
    
    async def _send_notification(
        self,
        notification: NotificationStatus
    ) -> None:
        """Send notification through appropriate channel.
        
        Args:
            notification: Notification to send
        """
        if notification.cancelled:
            return
        
        try:
            # Get event details
            query = select(Event).where(
                Event.id == notification.event_id
            )
            result = await self.session.execute(query)
            event = result.scalar_one_or_none()
            
            if not event:
                return
            
            # Prepare message
            message = self._format_notification_message(
                event,
                notification
            )
            
            # Send through appropriate channel
            if (
                notification.channel == NotificationChannel.EMAIL
                and self.email_service
            ):
                await self.email_service.send_email(
                    user_id=notification.user_id,
                    subject=f"Event Reminder: {event.title}",
                    body=message
                )
            
            elif (
                notification.channel == NotificationChannel.SMS
                and self.sms_service
            ):
                await self.sms_service.send_sms(
                    user_id=notification.user_id,
                    message=message
                )
            
            elif (
                notification.channel == NotificationChannel.PUSH
                and self.push_service
            ):
                await self.push_service.send_push(
                    user_id=notification.user_id,
                    title=event.title,
                    body=message
                )
            
            # Mark as sent
            notification.sent = True
            notification.sent_time = datetime.now()
            await self.session.commit()
            
        except Exception as e:
            # Log error but don't re-raise
            print(f"Error sending notification: {str(e)}")
    
    def _format_notification_message(
        self,
        event: Event,
        notification: NotificationStatus
    ) -> str:
        """Format notification message.
        
        Args:
            event: Event
            notification: Notification status
            
        Returns:
            Formatted message
        """
        # Format time until event
        if notification.reminder_unit == "minutes":
            time_str = (
                f"{notification.reminder_amount} minute"
                + ("s" if notification.reminder_amount > 1 else "")
            )
        elif notification.reminder_unit == "hours":
            time_str = (
                f"{notification.reminder_amount} hour"
                + ("s" if notification.reminder_amount > 1 else "")
            )
        elif notification.reminder_unit == "days":
            time_str = (
                f"{notification.reminder_amount} day"
                + ("s" if notification.reminder_amount > 1 else "")
            )
        else:
            time_str = (
                f"{notification.reminder_amount} week"
                + ("s" if notification.reminder_amount > 1 else "")
            )
        
        # Build message
        message = (
            f"Reminder: {event.title} starts in {time_str}\n"
            f"When: {event.start_time.strftime('%Y-%m-%d %H:%M')}\n"
        )
        
        if event.location:
            message += f"Where: {event.location}\n"
        
        if event.description:
            message += f"\n{event.description}"
        
        return message
