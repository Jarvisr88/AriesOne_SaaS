"""
Calendar Sharing Service Module

This module handles calendar sharing and permissions.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class SharePermission(str, Enum):
    """Share permission types"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class ShareType(str, Enum):
    """Share type enumeration"""
    USER = "user"
    GROUP = "group"
    PUBLIC = "public"

class ShareStatus(str, Enum):
    """Share status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"

class CalendarShare(BaseModel):
    """Calendar share definition"""
    share_id: UUID = Field(default_factory=uuid4)
    calendar_id: UUID
    owner_id: str
    share_type: ShareType
    target_id: str
    permission: SharePermission
    status: ShareStatus = ShareStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

class ShareInvitation(BaseModel):
    """Share invitation definition"""
    invitation_id: UUID = Field(default_factory=uuid4)
    share_id: UUID
    email: str
    message: Optional[str] = None
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

class CalendarSharingService:
    """Service for calendar sharing"""
    
    def __init__(self):
        """Initialize sharing service"""
        self._shares: Dict[UUID, CalendarShare] = {}
        self._invitations: Dict[UUID, ShareInvitation] = {}
        self._handlers: Dict[str, callable] = {}

    async def share_calendar(
        self,
        calendar_id: UUID,
        owner_id: str,
        share_type: ShareType,
        target_id: str,
        permission: SharePermission,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> CalendarShare:
        """Share calendar with user or group"""
        share = CalendarShare(
            calendar_id=calendar_id,
            owner_id=owner_id,
            share_type=share_type,
            target_id=target_id,
            permission=permission,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self._shares[share.share_id] = share
        return share

    async def send_invitation(
        self,
        share_id: UUID,
        email: str,
        message: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> ShareInvitation:
        """Send calendar share invitation"""
        share = self._shares.get(share_id)
        if not share:
            raise ValueError(f"Share not found: {share_id}")
        
        invitation = ShareInvitation(
            share_id=share_id,
            email=email,
            message=message,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self._invitations[invitation.invitation_id] = invitation
        
        # Notify handlers
        await self._notify_handlers("invitation_created", invitation)
        
        return invitation

    async def accept_share(
        self,
        share_id: UUID,
        user_id: str
    ) -> CalendarShare:
        """Accept calendar share"""
        share = self._shares.get(share_id)
        if not share:
            raise ValueError(f"Share not found: {share_id}")
        
        if share.target_id != user_id:
            raise ValueError("User is not the share target")
        
        if share.status != ShareStatus.PENDING:
            raise ValueError(f"Share is not pending: {share.status}")
        
        share.status = ShareStatus.ACCEPTED
        
        # Notify handlers
        await self._notify_handlers("share_accepted", share)
        
        return share

    async def decline_share(
        self,
        share_id: UUID,
        user_id: str
    ) -> CalendarShare:
        """Decline calendar share"""
        share = self._shares.get(share_id)
        if not share:
            raise ValueError(f"Share not found: {share_id}")
        
        if share.target_id != user_id:
            raise ValueError("User is not the share target")
        
        if share.status != ShareStatus.PENDING:
            raise ValueError(f"Share is not pending: {share.status}")
        
        share.status = ShareStatus.DECLINED
        
        # Notify handlers
        await self._notify_handlers("share_declined", share)
        
        return share

    async def revoke_share(
        self,
        share_id: UUID,
        owner_id: str
    ) -> CalendarShare:
        """Revoke calendar share"""
        share = self._shares.get(share_id)
        if not share:
            raise ValueError(f"Share not found: {share_id}")
        
        if share.owner_id != owner_id:
            raise ValueError("User is not the share owner")
        
        share.status = ShareStatus.REVOKED
        
        # Notify handlers
        await self._notify_handlers("share_revoked", share)
        
        return share

    async def get_calendar_shares(
        self,
        calendar_id: UUID
    ) -> List[CalendarShare]:
        """Get all shares for calendar"""
        return [
            s for s in self._shares.values()
            if s.calendar_id == calendar_id
        ]

    async def get_user_shares(
        self,
        user_id: str,
        include_owned: bool = True
    ) -> List[CalendarShare]:
        """Get all shares for user"""
        shares = []
        
        if include_owned:
            shares.extend([
                s for s in self._shares.values()
                if s.owner_id == user_id
            ])
        
        shares.extend([
            s for s in self._shares.values()
            if s.target_id == user_id and s.status == ShareStatus.ACCEPTED
        ])
        
        return shares

    async def check_permission(
        self,
        calendar_id: UUID,
        user_id: str,
        required_permission: SharePermission
    ) -> bool:
        """Check user's permission for calendar"""
        shares = [
            s for s in self._shares.values()
            if s.calendar_id == calendar_id and
            s.target_id == user_id and
            s.status == ShareStatus.ACCEPTED
        ]
        
        if not shares:
            return False
        
        # Get highest permission level
        permissions = {
            SharePermission.READ: 1,
            SharePermission.WRITE: 2,
            SharePermission.ADMIN: 3
        }
        
        required_level = permissions[required_permission]
        max_level = max(permissions[s.permission] for s in shares)
        
        return max_level >= required_level

    async def register_handler(
        self,
        event_type: str,
        handler: callable
    ):
        """Register event handler"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def _notify_handlers(
        self,
        event_type: str,
        data: Any
    ):
        """Notify event handlers"""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    await handler(data)
                except Exception as e:
                    print(f"Error in share event handler: {e}")
                    continue
