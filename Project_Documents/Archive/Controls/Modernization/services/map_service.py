"""
Map Service Module
Provides business logic for map operations.
"""
from typing import List, Dict, Optional
import aiohttp
from ..models.map_model import (
    MapProvider,
    MapProviderConfig,
    MapSearchResult,
    MapLocation,
    MapCoordinates,
    Address
)

class MapService:
    """Service for map operations."""
    
    def __init__(self, provider_configs: Dict[MapProvider, MapProviderConfig]):
        """
        Initialize map service.
        
        Args:
            provider_configs: Map provider configurations
        """
        self.provider_configs = provider_configs
        
    async def search_address(
        self,
        query: str,
        provider: Optional[MapProvider] = None
    ) -> List[MapSearchResult]:
        """
        Search for addresses using map providers.
        
        Args:
            query: Address search query
            provider: Optional specific provider to use
            
        Returns:
            List of search results
        """
        results = []
        providers = [provider] if provider else MapProvider
        
        for p in providers:
            if p not in self.provider_configs or not self.provider_configs[p].enabled:
                continue
                
            config = self.provider_configs[p]
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        str(config.base_url),
                        params={
                            'query': query,
                            'key': config.api_key
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            results.extend(self._parse_search_results(data, p))
            except Exception as e:
                print(f"Error searching with provider {p}: {str(e)}")
                
        return sorted(results, key=lambda x: x.confidence_score, reverse=True)
    
    async def geocode_address(
        self,
        address: Address,
        provider: Optional[MapProvider] = None
    ) -> MapSearchResult:
        """
        Geocode address to get coordinates.
        
        Args:
            address: Address to geocode
            provider: Optional specific provider to use
            
        Returns:
            Geocoding result
            
        Raises:
            ValueError: If geocoding fails
        """
        formatted_address = (
            f"{address.address_line1}, "
            f"{address.city}, {address.state} {address.zip_code}"
        )
        
        results = await self.search_address(formatted_address, provider)
        if not results:
            raise ValueError("Could not geocode address")
            
        return results[0]
    
    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
        provider: Optional[MapProvider] = None
    ) -> List[Address]:
        """
        Reverse geocode coordinates to get addresses.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            provider: Optional specific provider to use
            
        Returns:
            List of possible addresses
        """
        results = []
        providers = [provider] if provider else MapProvider
        
        for p in providers:
            if p not in self.provider_configs or not self.provider_configs[p].enabled:
                continue
                
            config = self.provider_configs[p]
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        str(config.base_url),
                        params={
                            'lat': latitude,
                            'lon': longitude,
                            'key': config.api_key
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            results.extend(self._parse_reverse_results(data))
            except Exception as e:
                print(f"Error reverse geocoding with provider {p}: {str(e)}")
                
        return results
    
    def _parse_search_results(
        self,
        data: dict,
        provider: MapProvider
    ) -> List[MapSearchResult]:
        """
        Parse provider-specific search results.
        
        Args:
            data: Raw provider response
            provider: Map provider
            
        Returns:
            List of parsed results
        """
        results = []
        
        if provider == MapProvider.GOOGLE:
            for item in data.get('results', []):
                location = MapLocation(
                    address=self._parse_google_address(item),
                    coordinates=MapCoordinates(
                        latitude=item['geometry']['location']['lat'],
                        longitude=item['geometry']['location']['lng']
                    ),
                    formatted_address=item.get('formatted_address'),
                    place_id=item.get('place_id')
                )
                results.append(MapSearchResult(
                    location=location,
                    provider=provider,
                    confidence_score=self._calculate_confidence(item),
                    alternatives=[]
                ))
                
        # Add similar parsing for other providers
                
        return results
    
    def _parse_reverse_results(self, data: dict) -> List[Address]:
        """
        Parse provider-specific reverse geocoding results.
        
        Args:
            data: Raw provider response
            
        Returns:
            List of parsed addresses
        """
        # Implementation depends on provider response format
        pass
    
    def _parse_google_address(self, item: dict) -> Address:
        """
        Parse Google Maps address components.
        
        Args:
            item: Google Maps result item
            
        Returns:
            Parsed address
        """
        components = item['address_components']
        address = Address(
            address_line1="",
            city="",
            state="",
            zip_code=""
        )
        
        for component in components:
            types = component['types']
            if 'street_number' in types:
                address.address_line1 = component['long_name']
            elif 'route' in types:
                address.address_line1 += f" {component['long_name']}"
            elif 'locality' in types:
                address.city = component['long_name']
            elif 'administrative_area_level_1' in types:
                address.state = component['short_name']
            elif 'postal_code' in types:
                address.zip_code = component['long_name']
                
        return address
    
    def _calculate_confidence(self, item: dict) -> float:
        """
        Calculate confidence score for search result.
        
        Args:
            item: Provider result item
            
        Returns:
            Confidence score between 0 and 1
        """
        # Implementation depends on provider result format
        return 1.0
