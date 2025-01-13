"""
Medicaid Service Module

This module implements the Medicaid portal integration.
"""
from datetime import datetime
import json
from typing import Dict, Optional
from uuid import uuid4

from fastapi import HTTPException
import httpx
from pydantic import BaseModel

from .payer_interface import PayerInterface, EligibilityRequest, EligibilityResponse
from ..models.credentials import MedicaidCredentials
from ..config import Settings


class MedicaidService(PayerInterface):
    """Medicaid portal service implementation."""

    def __init__(self, credentials: MedicaidCredentials, settings: Settings):
        """Initialize the Medicaid service."""
        self.credentials = credentials
        self.settings = settings
        self.base_url = settings.medicaid_portal_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.medicaid_timeout,
            verify=settings.ssl_verify
        )

    async def verify_eligibility(
        self, 
        request: EligibilityRequest
    ) -> EligibilityResponse:
        """Verify Medicaid eligibility."""
        try:
            # Transform request to Medicaid format
            medicaid_request = self._transform_to_medicaid(request)
            
            # Call Medicaid service
            async with self.client as client:
                response = await client.post(
                    "/eligibility/verify",
                    json=medicaid_request,
                    headers=self._get_auth_headers()
                )
                response.raise_for_status()
                
            # Transform response
            return self._transform_from_medicaid(response.json())
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Medicaid portal service error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error processing Medicaid eligibility: {str(e)}"
            )

    async def validate_credentials(self) -> bool:
        """Validate Medicaid credentials."""
        try:
            async with self.client as client:
                response = await client.post(
                    "/auth/validate",
                    headers=self._get_auth_headers()
                )
                return response.status_code == 200
        except Exception:
            return False

    async def check_service_availability(self) -> bool:
        """Check Medicaid portal availability."""
        try:
            async with self.client as client:
                response = await client.get("/health")
                return response.status_code == 200
        except Exception:
            return False

    async def get_service_metrics(self) -> Dict:
        """Get Medicaid service metrics."""
        return {
            "service": "Medicaid Portal",
            "status": await self.check_service_availability(),
            "credentials_valid": await self.validate_credentials(),
            "timestamp": datetime.utcnow()
        }

    def _get_auth_headers(self) -> Dict:
        """Get authentication headers for Medicaid portal."""
        return {
            "Authorization": f"Bearer {self.credentials.token}",
            "X-Correlation-ID": str(uuid4()),
            "X-State-Code": self.credentials.state_code,
            "X-Facility-ID": self.credentials.facility_id
        }

    def _transform_to_medicaid(self, request: EligibilityRequest) -> Dict:
        """Transform generic request to Medicaid format."""
        return {
            "memberId": request.subscriber_id,
            "providerNPI": request.provider_npi,
            "dateOfService": request.service_date.isoformat(),
            "serviceTypes": request.service_type_codes,
            "dependentInfo": {
                "code": request.dependent_code
            } if request.dependent_code else None,
            "additionalData": request.additional_info
        }

    def _transform_from_medicaid(self, medicaid_response: Dict) -> EligibilityResponse:
        """Transform Medicaid response to generic format."""
        return EligibilityResponse(
            is_eligible=medicaid_response.get("isEligible", False),
            coverage_status=medicaid_response.get("coverageStatus", "unknown"),
            plan_info=medicaid_response.get("planInformation", {}),
            benefits=medicaid_response.get("benefitDetails", {}),
            deductible=medicaid_response.get("financials", {}).get("deductible"),
            copay=medicaid_response.get("financials", {}).get("copay"),
            coinsurance=medicaid_response.get("financials", {}).get("coinsurance"),
            response_code=medicaid_response.get("responseCode", "unknown"),
            response_message=medicaid_response.get("message", ""),
            trace_id=uuid4(),
            raw_response=medicaid_response
        )
