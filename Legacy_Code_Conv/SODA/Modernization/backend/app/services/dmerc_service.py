"""DMERC service for business logic operations."""

from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status

from ..core.metrics import MetricsService
from ..repositories.dmerc_repository import DMERCRepository
from ..domain.models.dmerc import (
    DMERCForm,
    DMERCFormType,
    DMERCStatus,
    DMERCAttachment,
    DMERCHistory
)
from .base_service import BaseService

class DMERCService(BaseService[DMERCForm]):
    """Service for DMERC form operations."""

    def __init__(
        self,
        repository: DMERCRepository,
        metrics: Optional[MetricsService] = None
    ):
        """Initialize DMERC service."""
        super().__init__(repository, metrics)
        self.repository: DMERCRepository = repository

    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate DMERC form data."""
        required_fields = ["form_type", "patient_id", "organization_id"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        # Validate form type
        try:
            DMERCFormType(data["form_type"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid form type"
            )

    async def create_form(
        self,
        data: Dict[str, Any],
        created_by_id: UUID
    ) -> DMERCForm:
        """Create new DMERC form."""
        self.validate_data(data)

        # Set default values
        data.setdefault("status", DMERCStatus.DRAFT)
        data["created_by_id"] = created_by_id

        # Generate form number
        data["form_number"] = await self._generate_form_number(
            data["organization_id"],
            data["form_type"]
        )

        form = await self.create(data)
        if self.metrics:
            self.metrics.increment(f"dmerc.created.{data['form_type']}")

        return form

    async def update_form(
        self,
        form_id: UUID,
        data: Dict[str, Any],
        updated_by_id: UUID
    ) -> DMERCForm:
        """Update DMERC form."""
        form = await self.get_by_id(form_id)

        # Only allow updating draft forms
        if form.status != DMERCStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft forms can be updated"
            )

        data["updated_by_id"] = updated_by_id
        return await self.update(form_id, data)

    async def submit_form(
        self,
        form_id: UUID,
        submitted_by_id: UUID,
        notes: Optional[str] = None
    ) -> DMERCForm:
        """Submit DMERC form for review."""
        form = await self.get_by_id(form_id)

        # Verify form is in draft status
        if form.status != DMERCStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft forms can be submitted"
            )

        # Update form status
        updated = await self.repository.update_status(
            form_id,
            DMERCStatus.SUBMITTED,
            submitted_by_id,
            notes
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error submitting form"
            )

        if self.metrics:
            self.metrics.increment("dmerc.submitted")

        return updated

    async def approve_form(
        self,
        form_id: UUID,
        approved_by_id: UUID,
        notes: Optional[str] = None
    ) -> DMERCForm:
        """Approve DMERC form."""
        form = await self.get_by_id(form_id)

        # Verify form is in submitted status
        if form.status != DMERCStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted forms can be approved"
            )

        # Update form status
        updated = await self.repository.update_status(
            form_id,
            DMERCStatus.APPROVED,
            approved_by_id,
            notes
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error approving form"
            )

        if self.metrics:
            self.metrics.increment("dmerc.approved")

        return updated

    async def deny_form(
        self,
        form_id: UUID,
        denied_by_id: UUID,
        notes: str
    ) -> DMERCForm:
        """Deny DMERC form."""
        form = await self.get_by_id(form_id)

        # Verify form is in submitted status
        if form.status != DMERCStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted forms can be denied"
            )

        if not notes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Denial reason is required"
            )

        # Update form status
        updated = await self.repository.update_status(
            form_id,
            DMERCStatus.DENIED,
            denied_by_id,
            notes
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error denying form"
            )

        if self.metrics:
            self.metrics.increment("dmerc.denied")

        return updated

    async def add_attachment(
        self,
        form_id: UUID,
        file_name: str,
        file_type: str,
        file_size: int,
        file_path: str,
        uploaded_by_id: UUID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DMERCAttachment:
        """Add attachment to form."""
        form = await self.get_by_id(form_id)

        # Only allow attachments to non-finalized forms
        if form.status in [DMERCStatus.APPROVED, DMERCStatus.EXPIRED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add attachments to finalized forms"
            )

        attachment = await self.repository.add_attachment(
            form_id,
            file_name,
            file_type,
            file_size,
            file_path,
            uploaded_by_id,
            metadata
        )
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error adding attachment"
            )

        if self.metrics:
            self.metrics.increment("dmerc.attachment.added")
            self.metrics.gauge("dmerc.attachment.size", file_size)

        return attachment

    async def get_form_history(
        self,
        form_id: UUID,
        offset: int = 0,
        limit: int = 100
    ) -> List[DMERCHistory]:
        """Get form history."""
        await self.get_by_id(form_id)  # Verify form exists
        return await self.repository.get_form_history(
            form_id,
            offset=offset,
            limit=limit
        )

    async def get_form_attachments(
        self,
        form_id: UUID
    ) -> List[DMERCAttachment]:
        """Get form attachments."""
        await self.get_by_id(form_id)  # Verify form exists
        return await self.repository.get_form_attachments(form_id)

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
        return await self.repository.search_forms(
            organization_id,
            search_term,
            form_type=form_type,
            status=status,
            offset=offset,
            limit=limit
        )

    async def _generate_form_number(
        self,
        organization_id: UUID,
        form_type: DMERCFormType
    ) -> str:
        """Generate unique form number."""
        # Get count of forms for this org and type
        count = await self.repository.count(
            DMERCForm.organization_id == organization_id,
            DMERCForm.form_type == form_type
        )

        # Format: ORG-TYPE-YYYYMMDD-SEQUENCE
        return (
            f"{organization_id.hex[:6]}-"
            f"{form_type.value}-"
            f"{datetime.utcnow().strftime('%Y%m%d')}-"
            f"{count + 1:04d}"
        )
