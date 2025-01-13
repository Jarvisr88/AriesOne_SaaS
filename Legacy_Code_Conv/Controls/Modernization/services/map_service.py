from typing import List, Optional, Dict
from abc import ABC, abstractmethod
from fastapi import HTTPException
import aiohttp
from ..models.address import Address

class MapProvider(ABC):
    """Abstract base class for map providers"""
    
    @abstractmethod
    async def geocode(self, address: Address) -> Dict[str, float]:
        """Convert address to coordinates"""
        pass
    
    @abstractmethod
    async def get_map_url(self, address: Address) -> str:
        """Get URL for map visualization"""
        pass
    
    @abstractmethod
    async def validate_address(self, address: Address) -> bool:
        """Validate address exists"""
        pass

class GoogleMapsProvider(MapProvider):
    """Google Maps implementation of map provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    async def geocode(self, address: Address) -> Dict[str, float]:
        """Convert address to coordinates using Google Geocoding API"""
        async with aiohttp.ClientSession() as session:
            params = {
                'address': address.to_map_string(),
                'key': self.api_key
            }
            async with session.get(
                f"{self.base_url}/geocode/json",
                params=params
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Geocoding failed"
                    )
                data = await response.json()
                if data['status'] != 'OK':
                    raise HTTPException(
                        status_code=400,
                        detail=f"Geocoding error: {data['status']}"
                    )
                location = data['results'][0]['geometry']['location']
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng']
                }
    
    async def get_map_url(self, address: Address) -> str:
        """Get Google Maps URL for address"""
        coords = await self.geocode(address)
        return (
            f"https://www.google.com/maps/search/?api=1&"
            f"query={coords['latitude']},{coords['longitude']}"
        )
    
    async def validate_address(self, address: Address) -> bool:
        """Validate address using Google Geocoding API"""
        try:
            await self.geocode(address)
            return True
        except HTTPException:
            return False

class MapService:
    """Service for managing map providers and operations"""
    
    def __init__(self):
        self.providers: Dict[str, MapProvider] = {}
    
    def register_provider(self, name: str, provider: MapProvider) -> None:
        """Register a new map provider"""
        self.providers[name] = provider
    
    def get_provider(self, name: str) -> MapProvider:
        """Get a specific map provider"""
        if name not in self.providers:
            raise ValueError(f"Map provider '{name}' not found")
        return self.providers[name]
    
    def get_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    async def validate_address(
        self,
        address: Address,
        provider_name: Optional[str] = None
    ) -> bool:
        """
        Validate address using specified provider
        or first available provider
        """
        if provider_name:
            provider = self.get_provider(provider_name)
            return await provider.validate_address(address)
        
        for provider in self.providers.values():
            try:
                if await provider.validate_address(address):
                    return True
            except:
                continue
        return False
