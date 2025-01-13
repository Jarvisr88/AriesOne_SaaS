"""
Audit Logging Service Module

This module provides comprehensive audit logging capabilities.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from fastapi import HTTPException

class AuditEventType(str, Enum):
    """Audit event type enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS = "access"
    ERROR = "error"
    SYSTEM = "system"
    CUSTOM = "custom"

class AuditEventSeverity(str, Enum):
    """Audit event severity enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditEvent(BaseModel):
    """Audit event definition"""
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: AuditEventType
    severity: AuditEventSeverity = AuditEventSeverity.INFO
    user_id: Optional[str] = None
    resource_type: str
    resource_id: Optional[str] = None
    action: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None

class AuditFilter(BaseModel):
    """Audit event filter"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    severities: Optional[List[AuditEventSeverity]] = None
    user_ids: Optional[List[str]] = None
    resource_types: Optional[List[str]] = None
    resource_ids: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    statuses: Optional[List[str]] = None
    correlation_ids: Optional[List[str]] = None

class AuditLoggingService:
    """Audit logging service"""
    
    def __init__(self):
        """Initialize audit logging service"""
        self._events: List[AuditEvent] = []
        self._event_handlers: Dict[str, List[callable]] = {}
        self._retention_days: int = 365  # Default retention period

    async def log_event(
        self,
        event_type: AuditEventType,
        resource_type: str,
        action: str,
        status: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        severity: AuditEventSeverity = AuditEventSeverity.INFO,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> AuditEvent:
        """Log an audit event"""
        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status=status,
            details=details or {},
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            correlation_id=correlation_id
        )
        
        # Store event
        self._events.append(event)
        
        # Notify handlers
        await self._notify_handlers("event_logged", event)
        
        return event

    async def query_events(
        self,
        filter_params: AuditFilter,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[AuditEvent]:
        """Query audit events"""
        events = self._events
        
        # Apply filters
        if filter_params.start_time:
            events = [e for e in events if e.timestamp >= filter_params.start_time]
        if filter_params.end_time:
            events = [e for e in events if e.timestamp <= filter_params.end_time]
        if filter_params.event_types:
            events = [e for e in events if e.event_type in filter_params.event_types]
        if filter_params.severities:
            events = [e for e in events if e.severity in filter_params.severities]
        if filter_params.user_ids:
            events = [e for e in events if e.user_id in filter_params.user_ids]
        if filter_params.resource_types:
            events = [e for e in events if e.resource_type in filter_params.resource_types]
        if filter_params.resource_ids:
            events = [e for e in events if e.resource_id in filter_params.resource_ids]
        if filter_params.actions:
            events = [e for e in events if e.action in filter_params.actions]
        if filter_params.statuses:
            events = [e for e in events if e.status in filter_params.statuses]
        if filter_params.correlation_ids:
            events = [e for e in events if e.correlation_id in filter_params.correlation_ids]
        
        # Apply pagination
        if offset is not None:
            events = events[offset:]
        if limit is not None:
            events = events[:limit]
        
        return events

    async def register_event_handler(
        self,
        event_type: str,
        handler: callable
    ):
        """Register an event handler"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    async def set_retention_period(
        self,
        days: int
    ):
        """Set event retention period"""
        if days < 1:
            raise ValueError("Retention period must be at least 1 day")
        self._retention_days = days

    async def cleanup_old_events(self):
        """Clean up events older than retention period"""
        cutoff_date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        self._events = [
            e for e in self._events
            if (cutoff_date - e.timestamp).days < self._retention_days
        ]

    async def _notify_handlers(
        self,
        event_type: str,
        event: AuditEvent
    ):
        """Notify event handlers"""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"Error in audit event handler: {e}")
                    continue
