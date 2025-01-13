"""
Models for void management.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class VoidAction(str, Enum):
    """Void action enumeration."""
    VOID = "void"
    REPLACEMENT = "replacement"


class VoidBase(BaseModel):
    """Base void model."""
    claim_number: str = Field(
        ...,
        description="Claim number to void"
    )
    action: VoidAction = Field(
        ...,
        description="Void action"
    )
    reason: str = Field(
        ...,
        description="Void reason",
        min_length=1,
        max_length=500
    )


class VoidCreate(VoidBase):
    """Void creation model."""
    pass


class VoidUpdate(BaseModel):
    """Void update model."""
    reason: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500
    )


class Void(VoidBase):
    """Void model."""
    id: int = Field(..., description="Void identifier")
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Update timestamp"
    )
    created_by: str = Field(..., description="Creator")
    updated_by: str = Field(..., description="Updater")
    status: str = Field(..., description="Void status")

    class Config:
        """Pydantic config."""
        orm_mode = True
