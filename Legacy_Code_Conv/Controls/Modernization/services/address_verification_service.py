from typing import Dict, Optional
import httpx
from pydantic import BaseModel
import logging
from cache.cache_service import CacheService
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AddressComponents(BaseModel):
    street_number: str
    street_name: str
    city: str
    state: str
    postal_code: str
    country: str

class VerifiedAddress(BaseModel):
    formatted_address: str
    components: AddressComponents
    latitude: float
    longitude: float
    verification_source: str
    verification_status: str

class AddressVerificationService:
    def __init__(self):
        self.cache = CacheService()
        self.smarty_streets_api_key = "your-smarty-streets-api-key"  # Move to env
        self.usps_api_key = "your-usps-api-key"  # Move to env
        self.cache_ttl = timedelta(days=30)

    async def verify_address(self, address: str) -> Optional[VerifiedAddress]:
        """Verify address using multiple services with fallback"""
        # Check cache first
        cached_result = self.cache.get(f"verified_address:{address}")
        if cached_result:
            return VerifiedAddress(**cached_result)

        # Try primary service (SmartyStreets)
        try:
            result = await self._verify_with_smarty_streets(address)
            if result:
                self.cache.set(f"verified_address:{address}", result.dict(), self.cache_ttl)
                return result
        except Exception as e:
            logger.error(f"SmartyStreets verification failed: {e}")

        # Fallback to USPS
        try:
            result = await self._verify_with_usps(address)
            if result:
                self.cache.set(f"verified_address:{address}", result.dict(), self.cache_ttl)
                return result
        except Exception as e:
            logger.error(f"USPS verification failed: {e}")

        return None

    async def _verify_with_smarty_streets(self, address: str) -> Optional[VerifiedAddress]:
        """Verify address using SmartyStreets API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://us-street.api.smartystreets.com/street-address",
                    params={"auth-id": self.smarty_streets_api_key},
                    json={"street": address}
                )
                
                if response.status_code == 200:
                    data = response.json()[0]
                    return VerifiedAddress(
                        formatted_address=f"{data['delivery_line_1']}, {data['last_line']}",
                        components=AddressComponents(
                            street_number=data['components']['primary_number'],
                            street_name=data['components']['street_name'],
                            city=data['components']['city_name'],
                            state=data['components']['state_abbreviation'],
                            postal_code=data['components']['zipcode'],
                            country="USA"
                        ),
                        latitude=float(data['metadata']['latitude']),
                        longitude=float(data['metadata']['longitude']),
                        verification_source="SmartyStreets",
                        verification_status="verified"
                    )
            except Exception as e:
                logger.error(f"SmartyStreets API error: {e}")
                return None

    async def _verify_with_usps(self, address: str) -> Optional[VerifiedAddress]:
        """Verify address using USPS API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://secure.shippingapis.com/ShippingAPI.dll",
                    params={
                        "API": "Verify",
                        "XML": self._format_usps_request(address),
                        "UserID": self.usps_api_key
                    }
                )
                
                if response.status_code == 200:
                    data = self._parse_usps_response(response.text)
                    return VerifiedAddress(
                        formatted_address=data["formatted_address"],
                        components=AddressComponents(**data["components"]),
                        latitude=0.0,  # USPS doesn't provide coordinates
                        longitude=0.0,
                        verification_source="USPS",
                        verification_status="verified"
                    )
            except Exception as e:
                logger.error(f"USPS API error: {e}")
                return None

    def _format_usps_request(self, address: str) -> str:
        """Format address for USPS API request"""
        # Implementation would format the address into USPS XML format
        pass

    def _parse_usps_response(self, response_xml: str) -> Dict:
        """Parse USPS API response"""
        # Implementation would parse the USPS XML response
        pass

# Initialize global service
address_verification_service = AddressVerificationService()
