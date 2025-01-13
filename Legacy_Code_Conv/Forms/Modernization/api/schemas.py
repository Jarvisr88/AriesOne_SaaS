"""API schemas for request/response models.

This module defines Pydantic models for API validation.
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class FormBase(BaseModel):
    """Base form schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    schema: dict[str, Any] = Field(..., description="Form schema definition")


class FormCreate(FormBase):
    """Form creation schema."""
    pass


class FormUpdate(FormBase):
    """Form update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    schema: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class FormResponse(FormBase):
    """Form response schema."""
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class FormSubmissionBase(BaseModel):
    """Base form submission schema."""
    data: dict[str, Any] = Field(..., description="Form submission data")


class FormSubmissionCreate(FormSubmissionBase):
    """Form submission creation schema."""
    form_id: int
    company_id: int


class FormSubmissionResponse(FormSubmissionBase):
    """Form submission response schema."""
    id: int
    form_id: int
    submitted_by: int
    company_id: int
    submitted_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class CompanyBase(BaseModel):
    """Base company schema."""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    settings: Optional[dict[str, Any]] = None


class CompanyCreate(CompanyBase):
    """Company creation schema."""
    pass


class CompanyUpdate(CompanyBase):
    """Company update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    settings: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """Company response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class CompanyFormBase(BaseModel):
    """Base company form schema."""
    settings: Optional[dict[str, Any]] = None


class CompanyFormCreate(CompanyFormBase):
    """Company form creation schema."""
    company_id: int
    form_id: int


class CompanyFormUpdate(CompanyFormBase):
    """Company form update schema."""
    settings: dict[str, Any]
    is_active: Optional[bool] = None


class CompanyFormResponse(CompanyFormBase):
    """Company form response schema."""
    id: int
    company_id: int
    form_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True
