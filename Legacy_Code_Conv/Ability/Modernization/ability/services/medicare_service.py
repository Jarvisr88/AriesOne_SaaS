"""
Medicare Service Module

This module implements the Medicare HETS integration.
"""
from datetime import datetime
import json
from typing import Dict, Optional
from uuid import uuid4

from fastapi import HTTPException
import httpx
from pydantic import BaseModel

from .payer_interface import PayerInterface, EligibilityRequest, EligibilityResponse
from ..models.credentials import MedicareCredentials
from ..config import Settings


class MedicareService(PayerInterface):
    """Medicare HETS service implementation."""

    def __init__(self, credentials: MedicareCredentials, settings: Settings):
        """Initialize the Medicare service."""
        self.credentials = credentials
        self.settings = settings
        self.base_url = settings.medicare_hets_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.medicare_timeout,
            verify=settings.ssl_verify
        )

    async def verify_eligibility(
        self, 
        request: EligibilityRequest
    ) -> EligibilityResponse:
        """Verify Medicare eligibility."""
        try:
            # Transform request to HETS format
            hets_request = self._transform_to_hets(request)
            
            # Call HETS service
            async with self.client as client:
                response = await client.post(
                    "/eligibility",
                    json=hets_request,
                    headers=self._get_auth_headers()
                )
                response.raise_for_status()
                
            # Transform response
            return self._transform_from_hets(response.json())
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Medicare HETS service error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error processing Medicare eligibility: {str(e)}"
            )

    async def validate_credentials(self) -> bool:
        """Validate Medicare credentials."""
        try:
            async with self.client as client:
                response = await client.post(
                    "/validateCredentials",
                    headers=self._get_auth_headers()
                )
                return response.status_code == 200
        except Exception:
            return False

    async def check_service_availability(self) -> bool:
        """Check HETS service availability."""
        try:
            async with self.client as client:
                response = await client.get("/health")
                return response.status_code == 200
        except Exception:
            return False

    async def get_service_metrics(self) -> Dict:
        """Get HETS service metrics."""
        return {
            "service": "Medicare HETS",
            "status": await self.check_service_availability(),
            "credentials_valid": await self.validate_credentials(),
            "timestamp": datetime.utcnow()
        }

    def _get_auth_headers(self) -> Dict:
        """Get authentication headers for HETS."""
        return {
            "Authorization": f"Bearer {self.credentials.token}",
            "X-Correlation-ID": str(uuid4()),
            "X-Source-System": self.settings.system_identifier
        }

    def _transform_to_hets(self, request: EligibilityRequest) -> Dict:
        """Transform generic request to HETS format."""
        return {
            "subscriberId": request.subscriber_id,
            "providerNPI": request.provider_npi,
            "serviceDate": request.service_date.isoformat(),
            "serviceTypeCodes": request.service_type_codes,
            "dependentCode": request.dependent_code,
            "additionalInfo": request.additional_info
        }

    def _transform_from_hets(self, hets_response: Dict) -> EligibilityResponse:
        """Transform HETS response to generic format."""
        return EligibilityResponse(
            is_eligible=hets_response.get("eligible", False),
            coverage_status=hets_response.get("coverageStatus", "unknown"),
            plan_info=hets_response.get("planInfo", {}),
            benefits=hets_response.get("benefits", {}),
            deductible=hets_response.get("deductible"),
            copay=hets_response.get("copay"),
            coinsurance=hets_response.get("coinsurance"),
            response_code=hets_response.get("responseCode", "unknown"),
            response_message=hets_response.get("responseMessage", ""),
            trace_id=uuid4(),
            raw_response=hets_response
        )
