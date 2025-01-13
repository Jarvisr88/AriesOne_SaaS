"""Session schema module."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator
from decimal import Decimal

from core.models.session import SessionStatus, PaymentStatus

class SessionBase(BaseModel):
    """Base schema for Session data."""
    
    company_id: UUID
    location_id: UUID
    patient_id: UUID
    provider_id: Optional[UUID] = None
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    status: SessionStatus = SessionStatus.SCHEDULED
    payment_status: PaymentStatus = PaymentStatus.PENDING
    amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    notes: Optional[str] = None

    @validator('scheduled_end')
    def end_after_start(cls, v, values):
        """Validate that end time is after start time."""
        if 'scheduled_start' in values and v <= values['scheduled_start']:
            raise ValueError('scheduled_end must be after scheduled_start')
        return v

    @validator('actual_end')
    def actual_end_after_start(cls, v, values):
        """Validate that actual end time is after actual start time."""
        if v and 'actual_start' in values and values['actual_start'] and v <= values['actual_start']:
            raise ValueError('actual_end must be after actual_start')
        return v

class SessionCreate(SessionBase):
    """Schema for creating a Session."""
    pass

class SessionUpdate(SessionBase):
    """Schema for updating a Session."""
    company_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    patient_id: Optional[UUID] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None

class SessionInDB(SessionBase):
    """Schema for Session data from database."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True
