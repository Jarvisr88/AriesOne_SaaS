"""
Private Payer Service Module

This module implements the private payer API integration.
"""
from datetime import datetime
import json
from typing import Dict, Optional
from uuid import uuid4

from fastapi import HTTPException
import httpx
from pydantic import BaseModel

from .payer_interface import PayerInterface, EligibilityRequest, EligibilityResponse
from ..models.credentials import PrivatePayerCredentials
from ..config import Settings


class PrivatePayerService(PayerInterface):
    """Private payer service implementation."""

    def __init__(self, credentials: PrivatePayerCredentials, settings: Settings):
        """Initialize the private payer service."""
        self.credentials = credentials
        self.settings = settings
        self.base_url = settings.private_payer_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.private_payer_timeout,
            verify=settings.ssl_verify
        )

    async def verify_eligibility(
        self, 
        request: EligibilityRequest
    ) -> EligibilityResponse:
        """Verify private payer eligibility."""
        try:
            # Transform request to payer format
            payer_request = self._transform_to_payer(request)
            
            # Call payer service
            async with self.client as client:
                response = await client.post(
                    f"/payers/{self.credentials.payer_id}/eligibility",
                    json=payer_request,
                    headers=self._get_auth_headers()
                )
                response.raise_for_status()
                
            # Transform response
            return self._transform_from_payer(response.json())
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Private payer service error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error processing private payer eligibility: {str(e)}"
            )

    async def validate_credentials(self) -> bool:
        """Validate private payer credentials."""
        try:
            async with self.client as client:
                response = await client.post(
                    f"/payers/{self.credentials.payer_id}/auth/validate",
                    headers=self._get_auth_headers()
                )
                return response.status_code == 200
        except Exception:
            return False

    async def check_service_availability(self) -> bool:
        """Check private payer service availability."""
        try:
            async with self.client as client:
                response = await client.get(
                    f"/payers/{self.credentials.payer_id}/health"
                )
                return response.status_code == 200
        except Exception:
            return False

    async def get_service_metrics(self) -> Dict:
        """Get private payer service metrics."""
        return {
            "service": f"Private Payer {self.credentials.payer_id}",
            "status": await self.check_service_availability(),
            "credentials_valid": await self.validate_credentials(),
            "timestamp": datetime.utcnow()
        }

    def _get_auth_headers(self) -> Dict:
        """Get authentication headers for private payer."""
        return {
            "Authorization": f"Bearer {self.credentials.token}",
            "X-API-Key": self.credentials.api_key,
            "X-Correlation-ID": str(uuid4()),
            "X-Provider-ID": self.credentials.provider_id
        }

    def _transform_to_payer(self, request: EligibilityRequest) -> Dict:
        """Transform generic request to payer format."""
        return {
            "member": {
                "id": request.subscriber_id,
                "dependent_code": request.dependent_code
            },
            "provider": {
                "npi": request.provider_npi
            },
            "service": {
                "date": request.service_date.isoformat(),
                "types": request.service_type_codes
            },
            "additional_data": request.additional_info
        }

    def _transform_from_payer(self, payer_response: Dict) -> EligibilityResponse:
        """Transform payer response to generic format."""
        return EligibilityResponse(
            is_eligible=payer_response.get("eligibility", {}).get("status", False),
            coverage_status=payer_response.get("eligibility", {}).get("coverage", "unknown"),
            plan_info=payer_response.get("plan", {}),
            benefits=payer_response.get("benefits", {}),
            deductible=payer_response.get("financial", {}).get("deductible"),
            copay=payer_response.get("financial", {}).get("copay"),
            coinsurance=payer_response.get("financial", {}).get("coinsurance"),
            response_code=payer_response.get("meta", {}).get("code", "unknown"),
            response_message=payer_response.get("meta", {}).get("message", ""),
            trace_id=uuid4(),
            raw_response=payer_response
        )
