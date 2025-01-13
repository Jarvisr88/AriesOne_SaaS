"""
CMN (Certificate of Medical Necessity) Models Module

This module provides Pydantic models for CMN request/response handling.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, constr

class MedicareMainframe(BaseModel):
    """Medicare mainframe configuration model."""
    carrier_id: str = Field(..., description="Medicare carrier ID")
    facility_id: str = Field(..., description="Facility identifier")
    user_id: str = Field(..., description="User identifier")
    password: str = Field(..., description="Encrypted password")

class CmnSearchCriteria(BaseModel):
    """Search criteria for CMN requests."""
    npi: Optional[constr(min_length=10, max_length=10)] = Field(
        None, description="National Provider Identifier"
    )
    hic: Optional[str] = Field(None, description="Health Insurance Claim Number")
    hcpcs: Optional[str] = Field(None, description="HCPCS Code")
    mbi: Optional[constr(min_length=11, max_length=11)] = Field(
        None, description="Medicare Beneficiary Identifier"
    )
    max_results: Optional[int] = Field(
        100, ge=1, le=1000, description="Maximum number of results to return"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "npi": "1234567890",
                "mbi": "1EG4-TE5-MK73",
                "hcpcs": "E0470",
                "max_results": 100
            }
        }

class CmnRequest(BaseModel):
    """CMN request model."""
    request_id: UUID = Field(default_factory=UUID.uuid4, description="Unique request ID")
    medicare_mainframe: MedicareMainframe = Field(..., description="Mainframe configuration")
    search_criteria: CmnSearchCriteria = Field(..., description="Search criteria")
    mock_response: bool = Field(False, description="Use mock response for testing")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "medicare_mainframe": {
                    "carrier_id": "12345",
                    "facility_id": "67890",
                    "user_id": "TESTUSER",
                    "password": "encrypted_password"
                },
                "search_criteria": {
                    "npi": "1234567890",
                    "mbi": "1EG4-TE5-MK73",
                    "hcpcs": "E0470",
                    "max_results": 100
                },
                "mock_response": False
            }
        }

class CmnResponseEntry(BaseModel):
    """Individual CMN response entry."""
    entry_id: UUID = Field(default_factory=UUID.uuid4, description="Unique entry ID")
    npi: str = Field(..., description="Provider NPI")
    hic: Optional[str] = Field(None, description="Health Insurance Claim Number")
    mbi: str = Field(..., description="Medicare Beneficiary Identifier")
    hcpcs: str = Field(..., description="HCPCS Code")
    initial_date: datetime = Field(..., description="Initial certification date")
    recert_date: Optional[datetime] = Field(None, description="Recertification date")
    length_of_need: Optional[int] = Field(None, description="Length of need in months")
    status: str = Field(..., description="CMN status")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class CmnResponse(BaseModel):
    """CMN response model."""
    response_id: UUID = Field(default_factory=UUID.uuid4, description="Unique response ID")
    request_id: UUID = Field(..., description="Associated request ID")
    entries: List[CmnResponseEntry] = Field(default_factory=list, description="Response entries")
    total_count: int = Field(..., description="Total number of matching records")
    returned_count: int = Field(..., description="Number of records returned")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
