"""
Calendar Sync Service Module

This module handles calendar synchronization with external providers.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Protocol
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class CalendarProvider(str, Enum):
    """Calendar provider types"""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    ICALENDAR = "icalendar"
    EXCHANGE = "exchange"
    CALDAV = "caldav"

class SyncDirection(str, Enum):
    """Sync direction types"""
    IMPORT = "import"
    EXPORT = "export"
    BIDIRECTIONAL = "bidirectional"

class SyncStatus(str, Enum):
    """Sync status types"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class CalendarSync(BaseModel):
    """Calendar sync configuration"""
    sync_id: UUID = Field(default_factory=uuid4)
    provider: CalendarProvider
    direction: SyncDirection
    user_id: str
    calendar_id: str
    credentials: Dict[str, str]
    last_sync: Optional[datetime] = None
    sync_frequency: int  # minutes
    enabled: bool = True
    metadata: Dict[str, str] = Field(default_factory=dict)

class SyncResult(BaseModel):
    """Sync operation result"""
    sync_id: UUID
    status: SyncStatus
    events_added: int = 0
    events_updated: int = 0
    events_deleted: int = 0
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CalendarProvider(Protocol):
    """Calendar provider protocol"""
    
    async def authenticate(self, credentials: Dict[str, str]):
        """Authenticate with provider"""
        ...
    
    async def list_calendars(self) -> List[Dict[str, str]]:
        """List available calendars"""
        ...
    
    async def get_events(
        self,
        calendar_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """Get calendar events"""
        ...
    
    async def create_event(
        self,
        calendar_id: str,
        event: Dict
    ) -> Dict:
        """Create calendar event"""
        ...
    
    async def update_event(
        self,
        calendar_id: str,
        event_id: str,
        event: Dict
    ) -> Dict:
        """Update calendar event"""
        ...
    
    async def delete_event(
        self,
        calendar_id: str,
        event_id: str
    ):
        """Delete calendar event"""
        ...

class CalendarSyncService:
    """Service for calendar synchronization"""
    
    def __init__(self):
        """Initialize sync service"""
        self._syncs: Dict[UUID, CalendarSync] = {}
        self._providers: Dict[CalendarProvider, CalendarProvider] = {}

    async def register_provider(
        self,
        provider_type: CalendarProvider,
        provider: CalendarProvider
    ):
        """Register calendar provider"""
        self._providers[provider_type] = provider

    async def create_sync(
        self,
        provider: CalendarProvider,
        direction: SyncDirection,
        user_id: str,
        calendar_id: str,
        credentials: Dict[str, str],
        sync_frequency: int,
        metadata: Optional[Dict[str, str]] = None
    ) -> CalendarSync:
        """Create new sync configuration"""
        sync = CalendarSync(
            provider=provider,
            direction=direction,
            user_id=user_id,
            calendar_id=calendar_id,
            credentials=credentials,
            sync_frequency=sync_frequency,
            metadata=metadata or {}
        )
        
        self._syncs[sync.sync_id] = sync
        return sync

    async def perform_sync(
        self,
        sync_id: UUID,
        force: bool = False
    ) -> SyncResult:
        """Perform calendar sync"""
        sync = self._syncs.get(sync_id)
        if not sync:
            raise ValueError(f"Sync not found: {sync_id}")
        
        if not sync.enabled:
            raise ValueError(f"Sync is disabled: {sync_id}")
        
        # Check if sync is needed
        if not force and sync.last_sync:
            time_since_sync = (datetime.utcnow() - sync.last_sync).total_seconds() / 60
            if time_since_sync < sync.sync_frequency:
                return SyncResult(
                    sync_id=sync_id,
                    status=SyncStatus.COMPLETED,
                    events_added=0,
                    events_updated=0,
                    events_deleted=0
                )
        
        result = SyncResult(sync_id=sync_id, status=SyncStatus.IN_PROGRESS)
        
        try:
            provider = self._providers.get(sync.provider)
            if not provider:
                raise ValueError(f"Provider not found: {sync.provider}")
            
            # Authenticate
            await provider.authenticate(sync.credentials)
            
            # Perform sync based on direction
            if sync.direction in [SyncDirection.IMPORT, SyncDirection.BIDIRECTIONAL]:
                result = await self._import_events(sync, provider, result)
            
            if sync.direction in [SyncDirection.EXPORT, SyncDirection.BIDIRECTIONAL]:
                result = await self._export_events(sync, provider, result)
            
            # Update last sync time
            sync.last_sync = datetime.utcnow()
            result.status = SyncStatus.COMPLETED
            
        except Exception as e:
            result.status = SyncStatus.FAILED
            result.errors.append(str(e))
        
        return result

    async def _import_events(
        self,
        sync: CalendarSync,
        provider: CalendarProvider,
        result: SyncResult
    ) -> SyncResult:
        """Import events from external calendar"""
        # Implementation would handle importing events
        return result

    async def _export_events(
        self,
        sync: CalendarSync,
        provider: CalendarProvider,
        result: SyncResult
    ) -> SyncResult:
        """Export events to external calendar"""
        # Implementation would handle exporting events
        return result
