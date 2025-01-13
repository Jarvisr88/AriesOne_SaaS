"""
Address Service Module
Provides business logic for address operations.
"""
from typing import List
import aiohttp
from ..models.address_model import Address
from ..models.map_model import MapSearchResult, MapProvider, MapLocation
from .map_service import MapService

class AddressService:
    """Service for address operations."""
    
    def __init__(self, map_service: MapService):
        """
        Initialize address service.
        
        Args:
            map_service: Map service for geocoding
        """
        self.map_service = map_service
        
    async def validate_address(self, address: Address) -> Address:
        """
        Validate and standardize address.
        
        Args:
            address: Address to validate
            
        Returns:
            Validated address
            
        Raises:
            ValueError: If address is invalid
        """
        # Convert state to uppercase
        address.state = address.state.upper()
        
        # Format ZIP code
        if '-' not in address.zip_code and len(address.zip_code) > 5:
            address.zip_code = f"{address.zip_code[:5]}-{address.zip_code[5:]}"
            
        # Validate via geocoding
        result = await self.map_service.geocode_address(address)
        if result.confidence_score < 0.8:
            raise ValueError("Address could not be verified")
            
        return address
    
    async def standardize_address(self, address: Address) -> Address:
        """
        Standardize address format.
        
        Args:
            address: Address to standardize
            
        Returns:
            Standardized address
        """
        # Remove extra whitespace
        address.address_line1 = " ".join(address.address_line1.split())
        if address.address_line2:
            address.address_line2 = " ".join(address.address_line2.split())
        address.city = " ".join(address.city.split())
        
        # Convert to title case
        address.city = address.city.title()
        
        return address
    
    async def format_address(self, address: Address, format_type: str = "single_line") -> str:
        """
        Format address as string.
        
        Args:
            address: Address to format
            format_type: Format type (single_line, multi_line)
            
        Returns:
            Formatted address string
        """
        if format_type == "single_line":
            parts = [address.address_line1]
            if address.address_line2:
                parts.append(address.address_line2)
            parts.extend([address.city, address.state, address.zip_code])
            return ", ".join(parts)
        elif format_type == "multi_line":
            parts = [address.address_line1]
            if address.address_line2:
                parts.append(address.address_line2)
            parts.append(f"{address.city}, {address.state} {address.zip_code}")
            return "\n".join(parts)
        else:
            raise ValueError(f"Unknown format type: {format_type}")
    
    async def verify_address(self, address: Address) -> MapSearchResult:
        """
        Verify address using multiple providers.
        
        Args:
            address: Address to verify
            
        Returns:
            Verification result
            
        Raises:
            ValueError: If address cannot be verified
        """
        # Try multiple providers
        results = []
        for provider in MapProvider:
            try:
                result = await self.map_service.geocode_address(
                    address,
                    provider=provider
                )
                results.append(result)
            except Exception:
                continue
                
        if not results:
            raise ValueError("Address could not be verified by any provider")
            
        # Return result with highest confidence
        return max(results, key=lambda x: x.confidence_score)
