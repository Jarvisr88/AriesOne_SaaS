"""
Event Notifications Service Module

This module handles calendar event notifications and reminders.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Union
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class NotificationType(str, Enum):
    """Notification type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class NotificationStatus(str, Enum):
    """Notification status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ReminderInterval(BaseModel):
    """Reminder interval definition"""
    value: int
    unit: str  # minutes, hours, days

class NotificationTemplate(BaseModel):
    """Notification template definition"""
    template_id: UUID = Field(default_factory=uuid4)
    type: NotificationType
    subject: str
    body: str
    variables: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, str] = Field(default_factory=dict)

class EventNotification(BaseModel):
    """Event notification definition"""
    notification_id: UUID = Field(default_factory=uuid4)
    event_id: UUID
    user_id: str
    type: NotificationType
    template_id: UUID
    reminder_time: datetime
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

class NotificationPreference(BaseModel):
    """User notification preference"""
    user_id: str
    type: NotificationType
    enabled: bool = True
    channels: Dict[str, str] = Field(default_factory=dict)
    reminders: List[ReminderInterval] = Field(default_factory=list)

class EventNotificationService:
    """Service for event notifications"""
    
    def __init__(self):
        """Initialize notification service"""
        self._templates: Dict[UUID, NotificationTemplate] = {}
        self._notifications: Dict[UUID, EventNotification] = {}
        self._preferences: Dict[str, Dict[NotificationType, NotificationPreference]] = {}
        self._handlers: Dict[NotificationType, callable] = {}

    async def register_template(
        self,
        type: NotificationType,
        subject: str,
        body: str,
        variables: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> NotificationTemplate:
        """Register notification template"""
        template = NotificationTemplate(
            type=type,
            subject=subject,
            body=body,
            variables=variables or {},
            metadata=metadata or {}
        )
        
        self._templates[template.template_id] = template
        return template

    async def set_preference(
        self,
        user_id: str,
        type: NotificationType,
        enabled: bool = True,
        channels: Optional[Dict[str, str]] = None,
        reminders: Optional[List[ReminderInterval]] = None
    ) -> NotificationPreference:
        """Set user notification preference"""
        preference = NotificationPreference(
            user_id=user_id,
            type=type,
            enabled=enabled,
            channels=channels or {},
            reminders=reminders or []
        )
        
        if user_id not in self._preferences:
            self._preferences[user_id] = {}
        
        self._preferences[user_id][type] = preference
        return preference

    async def schedule_notification(
        self,
        event_id: UUID,
        user_id: str,
        type: NotificationType,
        template_id: UUID,
        reminder_time: datetime,
        metadata: Optional[Dict[str, str]] = None
    ) -> EventNotification:
        """Schedule event notification"""
        # Check if template exists
        if template_id not in self._templates:
            raise ValueError(f"Template not found: {template_id}")
        
        # Check user preferences
        user_prefs = self._preferences.get(user_id, {}).get(type)
        if not user_prefs or not user_prefs.enabled:
            return None
        
        notification = EventNotification(
            event_id=event_id,
            user_id=user_id,
            type=type,
            template_id=template_id,
            reminder_time=reminder_time,
            metadata=metadata or {}
        )
        
        self._notifications[notification.notification_id] = notification
        return notification

    async def cancel_notification(
        self,
        notification_id: UUID
    ):
        """Cancel scheduled notification"""
        notification = self._notifications.get(notification_id)
        if notification and notification.status == NotificationStatus.PENDING:
            notification.status = NotificationStatus.CANCELLED

    async def register_handler(
        self,
        type: NotificationType,
        handler: callable
    ):
        """Register notification handler"""
        self._handlers[type] = handler

    async def process_pending_notifications(
        self,
        batch_size: int = 100
    ) -> List[EventNotification]:
        """Process pending notifications"""
        now = datetime.utcnow()
        processed = []
        
        # Get pending notifications
        pending = [
            n for n in self._notifications.values()
            if n.status == NotificationStatus.PENDING and n.reminder_time <= now
        ][:batch_size]
        
        for notification in pending:
            try:
                # Get template
                template = self._templates[notification.template_id]
                
                # Get handler
                handler = self._handlers.get(notification.type)
                if not handler:
                    raise ValueError(f"Handler not found: {notification.type}")
                
                # Send notification
                await handler(notification, template)
                
                # Update status
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
                
            except Exception as e:
                notification.status = NotificationStatus.FAILED
                notification.error = str(e)
            
            processed.append(notification)
        
        return processed

    async def get_user_notifications(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[NotificationStatus] = None
    ) -> List[EventNotification]:
        """Get user notifications"""
        notifications = [
            n for n in self._notifications.values()
            if n.user_id == user_id
        ]
        
        if start_time:
            notifications = [n for n in notifications if n.reminder_time >= start_time]
        if end_time:
            notifications = [n for n in notifications if n.reminder_time <= end_time]
        if status:
            notifications = [n for n in notifications if n.status == status]
        
        return sorted(notifications, key=lambda x: x.reminder_time)
