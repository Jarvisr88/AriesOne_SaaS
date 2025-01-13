"""DMERC schemas."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from ...domain.models.dmerc import DMERCFormType, DMERCStatus

class DMERCFormBase(BaseModel):
    """Base DMERC form schema."""
    form_type: DMERCFormType
    patient_id: str
    organization_id: UUID
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DMERCFormCreate(DMERCFormBase):
    """DMERC form creation schema."""
    pass

class DMERCFormUpdate(BaseModel):
    """DMERC form update schema."""
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DMERCFormResponse(DMERCFormBase):
    """DMERC form response schema."""
    id: UUID
    form_number: str
    status: DMERCStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    denied_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_by_id: UUID
    updated_by_id: Optional[UUID] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class DMERCAttachmentBase(BaseModel):
    """Base DMERC attachment schema."""
    file_name: str
    file_type: str
    file_size: int
    metadata: Optional[Dict[str, Any]] = None

class DMERCAttachmentCreate(DMERCAttachmentBase):
    """DMERC attachment creation schema."""
    file_path: str

class DMERCAttachmentResponse(DMERCAttachmentBase):
    """DMERC attachment response schema."""
    id: UUID
    form_id: UUID
    file_path: str
    created_at: datetime
    uploaded_by_id: UUID

    class Config:
        """Pydantic config."""
        from_attributes = True

class DMERCHistoryResponse(BaseModel):
    """DMERC history response schema."""
    id: UUID
    form_id: UUID
    action: str
    changes: Dict[str, Any]
    created_at: datetime
    performed_by_id: UUID

    class Config:
        """Pydantic config."""
        from_attributes = True

class DMERCFormWithDetails(DMERCFormResponse):
    """DMERC form response with details schema."""
    attachments: List[DMERCAttachmentResponse]
    history: List[DMERCHistoryResponse]

class DMERCStatusUpdate(BaseModel):
    """DMERC status update schema."""
    notes: Optional[str] = None

class DMERCSearchParams(BaseModel):
    """DMERC search parameters schema."""
    search_term: str
    form_type: Optional[DMERCFormType] = None
    status: Optional[DMERCStatus] = None
    offset: int = 0
    limit: int = 100

class DMERCSearchResponse(BaseModel):
    """DMERC search response schema."""
    forms: List[DMERCFormResponse]
    total: int
