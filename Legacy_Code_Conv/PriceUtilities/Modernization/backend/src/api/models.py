"""
API request/response models for PriceUtilities Module.
"""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator

class PriceUpdateRequest(BaseModel):
    """Request model for price updates"""
    item_id: str = Field(..., description="Unique identifier for the item")
    base_price: Decimal = Field(..., description="Base price for the item")
    currency: str = Field(..., description="Three-letter currency code")
    quantity_breaks: Optional[Dict[int, Decimal]] = Field(None, description="Quantity discount breaks")
    effective_date: Optional[datetime] = Field(None, description="When the price becomes effective")
    icd_codes: Optional[List[str]] = Field(None, description="Associated ICD codes")

class BulkPriceUpdateRequest(BaseModel):
    """Request model for bulk price updates"""
    updates: List[PriceUpdateRequest] = Field(..., description="List of price updates")

class PriceCalculationRequest(BaseModel):
    """Request model for price calculations"""
    item_id: str = Field(..., description="Item to calculate price for")
    quantity: int = Field(..., gt=0, description="Quantity of items")
    icd_codes: Optional[List[str]] = Field(None, description="Applicable ICD codes")
    calculation_date: Optional[datetime] = Field(None, description="Date for calculation")

class AuditQueryParams(BaseModel):
    """Query parameters for audit log retrieval"""
    start_date: Optional[datetime] = Field(None, description="Start date for audit records")
    end_date: Optional[datetime] = Field(None, description="End date for audit records")
    entity_type: Optional[str] = Field(None, description="Type of entity to filter")
    entity_id: Optional[str] = Field(None, description="ID of entity to filter")
    action_type: Optional[str] = Field(None, description="Type of action to filter")
    user_id: Optional[str] = Field(None, description="User ID to filter")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records")
    offset: int = Field(0, ge=0, description="Number of records to skip")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    details: Optional[Dict] = Field(None, description="Additional error details")
    code: str = Field(..., description="Error code for client handling")
