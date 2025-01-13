"""
Payer Interface Module

This module defines the base interface for all payer integrations.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional, List
from uuid import UUID

from pydantic import BaseModel


class EligibilityRequest(BaseModel):
    """Base eligibility request model."""
    subscriber_id: str
    provider_npi: str
    service_date: datetime
    service_type_codes: List[str]
    dependent_code: Optional[str] = None
    additional_info: Optional[Dict] = None


class EligibilityResponse(BaseModel):
    """Base eligibility response model."""
    is_eligible: bool
    coverage_status: str
    plan_info: Dict
    benefits: Dict
    deductible: Optional[float]
    copay: Optional[float]
    coinsurance: Optional[float]
    response_code: str
    response_message: str
    trace_id: UUID
    raw_response: Optional[Dict] = None


class PayerInterface(ABC):
    """Abstract base class for payer integrations."""

    @abstractmethod
    async def verify_eligibility(
        self, 
        request: EligibilityRequest
    ) -> EligibilityResponse:
        """Verify eligibility with the payer system."""
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate the current credentials with the payer system."""
        pass

    @abstractmethod
    async def check_service_availability(self) -> bool:
        """Check if the payer service is available."""
        pass

    @abstractmethod
    async def get_service_metrics(self) -> Dict:
        """Get service performance metrics."""
        pass
