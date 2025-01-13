import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union
import xml.etree.ElementTree as ET
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import aiohttp
from fastapi import HTTPException

from app.models.medicare import MainframeResponse, MainframeError
from app.core.config import settings

logger = logging.getLogger(__name__)

class MainframeConnectionError(Exception):
    """Raised when connection to mainframe fails"""
    pass

class MainframeTimeoutError(Exception):
    """Raised when mainframe operation times out"""
    pass

class MainframeDataError(Exception):
    """Raised when there's an issue with data processing"""
    pass

class MainframeClient:
    def __init__(self):
        self.base_url = settings.MAINFRAME_BASE_URL
        self.username = settings.MAINFRAME_USERNAME
        self.password = settings.MAINFRAME_PASSWORD
        self.timeout = settings.MAINFRAME_TIMEOUT
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            base_url=self.base_url,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _xml_to_json(self, xml_data: str) -> dict:
        """Convert XML response to JSON format"""
        try:
            root = ET.fromstring(xml_data)
            return self._element_to_dict(root)
        except ET.ParseError as e:
            raise MainframeDataError(f"Failed to parse XML response: {str(e)}")

    def _element_to_dict(self, element: ET.Element) -> Union[Dict, str]:
        """Convert XML element to dictionary"""
        result = {}
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                result[child.tag] = self._element_to_dict(child)
        return result if result else element.text

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(
            (MainframeConnectionError, MainframeTimeoutError, aiohttp.ClientError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> MainframeResponse:
        """Make HTTP request to mainframe with retry mechanism"""
        if not self.session:
            raise MainframeConnectionError("Client session not initialized")

        start_time = datetime.now()
        try:
            async with self.session.request(
                method=method,
                url=endpoint,
                json=data,
                auth=aiohttp.BasicAuth(self.username, self.password),
            ) as response:
                response_time = (datetime.now() - start_time).total_seconds()
                
                if response.headers.get("Content-Type") == "application/xml":
                    text_response = await response.text()
                    response_data = self._xml_to_json(text_response)
                else:
                    response_data = await response.json()

                if response.status >= 400:
                    error = MainframeError(
                        code=str(response.status),
                        message=response_data.get("message", "Unknown error"),
                        details=response_data.get("details"),
                        timestamp=datetime.now().date(),
                        transaction_id=response_data.get("transaction_id"),
                    )
                    return MainframeResponse(
                        success=False,
                        error=error,
                        response_time=response_time,
                        transaction_id=response_data.get("transaction_id", ""),
                    )

                return MainframeResponse(
                    success=True,
                    data=response_data,
                    response_time=response_time,
                    transaction_id=response_data.get("transaction_id", ""),
                )

        except asyncio.TimeoutError as e:
            logger.error(f"Mainframe request timed out: {str(e)}")
            raise MainframeTimeoutError("Request timed out")
        except aiohttp.ClientError as e:
            logger.error(f"Mainframe connection error: {str(e)}")
            raise MainframeConnectionError(f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during mainframe request: {str(e)}")
            raise MainframeDataError(f"Data processing error: {str(e)}")

    async def get_beneficiary(self, medicare_id: str) -> MainframeResponse:
        """Get beneficiary information"""
        return await self._make_request(
            method="GET",
            endpoint=f"/beneficiary/{medicare_id}",
        )

    async def get_claim(self, claim_id: str) -> MainframeResponse:
        """Get claim information"""
        return await self._make_request(
            method="GET",
            endpoint=f"/claim/{claim_id}",
        )

    async def submit_claim(self, claim_data: dict) -> MainframeResponse:
        """Submit a new claim"""
        return await self._make_request(
            method="POST",
            endpoint="/claim",
            data=claim_data,
        )

    async def update_claim(self, claim_id: str, claim_data: dict) -> MainframeResponse:
        """Update an existing claim"""
        return await self._make_request(
            method="PUT",
            endpoint=f"/claim/{claim_id}",
            data=claim_data,
        )

    async def get_service_codes(self) -> MainframeResponse:
        """Get list of service codes"""
        return await self._make_request(
            method="GET",
            endpoint="/service-codes",
        )

    async def check_eligibility(self, medicare_id: str, service_code: str) -> MainframeResponse:
        """Check service eligibility for beneficiary"""
        return await self._make_request(
            method="GET",
            endpoint=f"/eligibility/{medicare_id}/{service_code}",
        )

    async def get_claim_status(self, claim_id: str) -> MainframeResponse:
        """Get claim processing status"""
        return await self._make_request(
            method="GET",
            endpoint=f"/claim/{claim_id}/status",
        )
