"""DMERC repository for database operations."""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.sql import Select

from ..core.database.base_repository import BaseRepository
from ..core.database.database import DatabaseService
from ..core.cache import CacheService
from ..core.metrics import MetricsService
from ..domain.models.dmerc import (
    DMERCForm,
    DMERCFormType,
    DMERCStatus,
    DMERCAttachment,
    DMERCHistory
)

class DMERCRepository(BaseRepository[DMERCForm]):
    """Repository for DMERC form operations."""

    def __init__(
        self,
        db: DatabaseService,
        cache: Optional[CacheService] = None,
        metrics: Optional[MetricsService] = None
    ):
        """Initialize DMERC repository."""
        super().__init__(db, DMERCForm, cache, metrics)
        self.cache_ttl = 1800  # 30 minutes for DMERC forms

    async def find_by_form_number(self, form_number: str) -> Optional[DMERCForm]:
        """Find form by form number."""
        return await self.find_one(DMERCForm.form_number == form_number)

    async def find_by_patient(
        self,
        patient_id: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[DMERCForm]:
        """Find forms by patient ID."""
        return await self.find_many(
            DMERCForm.patient_id == patient_id,
            offset=offset,
            limit=limit
        )

    async def find_by_organization(
        self,
        organization_id: UUID,
        offset: int = 0,
        limit: int = 100
    ) -> List[DMERCForm]:
        """Find forms by organization."""
        return await self.find_many(
            DMERCForm.organization_id == organization_id,
            offset=offset,
            limit=limit
        )

    async def find_by_status(
        self,
        status: DMERCStatus,
        organization_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[DMERCForm]:
        """Find forms by status."""
        conditions = [DMERCForm.status == status]
        if organization_id:
            conditions.append(DMERCForm.organization_id == organization_id)
        
        return await self.find_many(
            *conditions,
            offset=offset,
            limit=limit
        )

    async def find_expired_forms(
        self,
        organization_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[DMERCForm]:
        """Find expired forms."""
        conditions = [
            DMERCForm.expires_at <= datetime.utcnow(),
            DMERCForm.status != DMERCStatus.EXPIRED
        ]
        if organization_id:
            conditions.append(DMERCForm.organization_id == organization_id)
        
        return await self.find_many(
            *conditions,
            offset=offset,
            limit=limit
        )

    async def update_status(
        self,
        form_id: UUID,
        status: DMERCStatus,
        updated_by_id: UUID,
        notes: Optional[str] = None
    ) -> Optional[DMERCForm]:
        """Update form status."""
        try:
            async with self.db.transaction() as session:
                form = await session.get(DMERCForm, form_id)
                if not form:
                    return None

                # Update status and timestamps
                old_status = form.status
                form.status = status
                form.updated_by_id = updated_by_id
                
                if status == DMERCStatus.SUBMITTED:
                    form.submitted_at = datetime.utcnow()
                elif status == DMERCStatus.APPROVED:
                    form.approved_at = datetime.utcnow()
                elif status == DMERCStatus.DENIED:
                    form.denied_at = datetime.utcnow()
                
                if notes:
                    form.notes = notes

                # Create history entry
                history = DMERCHistory(
                    form_id=form_id,
                    performed_by_id=updated_by_id,
                    action=f"Status changed from {old_status.value} to {status.value}",
                    changes={
                        "old_status": old_status.value,
                        "new_status": status.value,
                        "notes": notes
                    }
                )
                session.add(history)
                
                await session.flush()
                await session.refresh(form)
                
                # Update cache
                await self._cache_entity(form)
                
                if self.metrics:
                    self.metrics.increment(f"dmerc.status.{status.value}")
                
                return form

        except Exception as e:
            self.logger.error(f"Error updating DMERC form status: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment("dmerc.error.update_status")
            return None

    async def add_attachment(
        self,
        form_id: UUID,
        file_name: str,
        file_type: str,
        file_size: int,
        file_path: str,
        uploaded_by_id: UUID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[DMERCAttachment]:
        """Add attachment to form."""
        try:
            async with self.db.transaction() as session:
                attachment = DMERCAttachment(
                    form_id=form_id,
                    file_name=file_name,
                    file_type=file_type,
                    file_size=file_size,
                    file_path=file_path,
                    uploaded_by_id=uploaded_by_id,
                    metadata=metadata
                )
                session.add(attachment)
                await session.flush()
                await session.refresh(attachment)
                
                if self.metrics:
                    self.metrics.increment("dmerc.attachment.added")
                    self.metrics.gauge("dmerc.attachment.size", file_size)
                
                return attachment

        except Exception as e:
            self.logger.error(f"Error adding DMERC attachment: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment("dmerc.error.add_attachment")
            return None

    async def get_form_history(
        self,
        form_id: UUID,
        offset: int = 0,
        limit: int = 100
    ) -> List[DMERCHistory]:
        """Get form history."""
        try:
            async with self.db.session() as session:
                query = (
                    select(DMERCHistory)
                    .where(DMERCHistory.form_id == form_id)
                    .order_by(desc(DMERCHistory.created_at))
                    .offset(offset)
                    .limit(limit)
                )
                
                result = await session.execute(query)
                return list(result.scalars().all())

        except Exception as e:
            self.logger.error(f"Error getting DMERC form history: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment("dmerc.error.get_history")
            return []

    async def get_form_attachments(
        self,
        form_id: UUID
    ) -> List[DMERCAttachment]:
        """Get form attachments."""
        try:
            async with self.db.session() as session:
                query = (
                    select(DMERCAttachment)
                    .where(DMERCAttachment.form_id == form_id)
                    .order_by(desc(DMERCAttachment.created_at))
                )
                
                result = await session.execute(query)
                return list(result.scalars().all())

        except Exception as e:
            self.logger.error(f"Error getting DMERC form attachments: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment("dmerc.error.get_attachments")
            return []

    async def search_forms(
        self,
        organization_id: UUID,
        search_term: str,
        form_type: Optional[DMERCFormType] = None,
        status: Optional[DMERCStatus] = None,
        offset: int = 0,
        limit: int = 100
    ) -> Tuple[List[DMERCForm], int]:
        """Search forms with filters."""
        try:
            conditions = [DMERCForm.organization_id == organization_id]
            
            # Add search condition
            search_pattern = f"%{search_term}%"
            conditions.append(
                or_(
                    DMERCForm.form_number.ilike(search_pattern),
                    DMERCForm.patient_id.ilike(search_pattern)
                )
            )
            
            # Add filters
            if form_type:
                conditions.append(DMERCForm.form_type == form_type)
            if status:
                conditions.append(DMERCForm.status == status)
            
            # Get total count
            total = await self.count(*conditions)
            
            # Get paginated results
            forms = await self.find_many(
                *conditions,
                offset=offset,
                limit=limit
            )
            
            return forms, total

        except Exception as e:
            self.logger.error(f"Error searching DMERC forms: {str(e)}", exc_info=True)
            if self.metrics:
                self.metrics.increment("dmerc.error.search")
            return [], 0
