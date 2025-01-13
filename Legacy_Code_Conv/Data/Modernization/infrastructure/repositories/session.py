"""Session repository implementation module."""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.session import Session, SessionStatus
from infrastructure.repositories.base import Repository

class SessionRepository(Repository[Session]):
    """Session repository implementation."""

    def __init__(self, session: AsyncSession):
        """Initialize repository.
        
        Args:
            session: Database session.
        """
        super().__init__(session, Session)

    async def get_by_date_range(
        self,
        company_id: UUID,
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None
    ) -> List[Session]:
        """Get sessions within date range.
        
        Args:
            company_id: Company ID.
            start_date: Start date.
            end_date: End date.
            location_id: Optional location ID filter.
            provider_id: Optional provider ID filter.
            
        Returns:
            List of sessions.
        """
        filters = [
            Session.company_id == company_id,
            Session.scheduled_start >= start_date,
            Session.scheduled_start <= end_date
        ]
        
        if location_id:
            filters.append(Session.location_id == location_id)
        if provider_id:
            filters.append(Session.provider_id == provider_id)

        result = await self._session.execute(
            select(Session).where(and_(*filters))
        )
        return list(result.scalars().all())

    async def get_upcoming_sessions(
        self,
        company_id: UUID,
        location_id: Optional[UUID] = None
    ) -> List[Session]:
        """Get upcoming sessions.
        
        Args:
            company_id: Company ID.
            location_id: Optional location ID filter.
            
        Returns:
            List of upcoming sessions.
        """
        filters = [
            Session.company_id == company_id,
            Session.scheduled_start >= datetime.now(),
            Session.status == SessionStatus.SCHEDULED
        ]
        
        if location_id:
            filters.append(Session.location_id == location_id)

        result = await self._session.execute(
            select(Session)
            .where(and_(*filters))
            .order_by(Session.scheduled_start)
        )
        return list(result.scalars().all())
