from datetime import datetime
from typing import List, Dict, Optional, Tuple
import aiohttp
import asyncio
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.maps import (
    MapProvider,
    GeocodingResult,
    TrafficData,
    MapStyle,
    ProviderStatus
)

class MapService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.providers = self._initialize_providers()
        self.active_provider = None
        self.fallback_queue = []
        self.provider_status = {}
        self.cache = {}
        self.style_config = settings.maps.style_config

    def _initialize_providers(self) -> Dict[str, MapProvider]:
        """
        Initialize map providers from configuration
        """
        providers = {}
        for provider_config in self.settings.maps.providers:
            providers[provider_config.name] = MapProvider(
                name=provider_config.name,
                api_key=provider_config.api_key,
                base_url=provider_config.base_url,
                priority=provider_config.priority
            )
        return providers

    async def get_geocoding(
        self,
        address: str,
        provider: Optional[str] = None
    ) -> GeocodingResult:
        """
        Get geocoding results with fallback support
        """
        try:
            if provider:
                return await self._geocode_with_provider(address, provider)

            # Try providers in priority order
            for provider in sorted(
                self.providers.values(),
                key=lambda x: x.priority
            ):
                try:
                    return await self._geocode_with_provider(
                        address,
                        provider.name
                    )
                except Exception as e:
                    logger.warning(
                        f"Geocoding failed with {provider.name}: {str(e)}"
                    )
                    continue

            raise HTTPException(
                status_code=500,
                detail="All geocoding providers failed"
            )

        except Exception as e:
            logger.error(f"Error in geocoding: {str(e)}")
            raise

    async def get_traffic_data(
        self,
        bounds: Dict[str, float],
        provider: Optional[str] = None
    ) -> TrafficData:
        """
        Get real-time traffic data
        """
        try:
            if provider:
                return await self._get_traffic_with_provider(bounds, provider)

            # Try providers in priority order
            for provider in sorted(
                self.providers.values(),
                key=lambda x: x.priority
            ):
                try:
                    return await self._get_traffic_with_provider(
                        bounds,
                        provider.name
                    )
                except Exception as e:
                    logger.warning(
                        f"Traffic data failed with {provider.name}: {str(e)}"
                    )
                    continue

            raise HTTPException(
                status_code=500,
                detail="All traffic providers failed"
            )

        except Exception as e:
            logger.error(f"Error getting traffic data: {str(e)}")
            raise

    async def get_map_style(
        self,
        style_name: str,
        provider: Optional[str] = None
    ) -> MapStyle:
        """
        Get custom map style configuration
        """
        try:
            # Check cache first
            cache_key = f"{style_name}_{provider}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            style = await MapStyle.get_or_none(
                name=style_name,
                provider=provider if provider else self.active_provider.name
            )

            if not style:
                style = await self._create_default_style(
                    style_name,
                    provider
                )

            self.cache[cache_key] = style
            return style

        except Exception as e:
            logger.error(f"Error getting map style: {str(e)}")
            raise

    async def update_provider_status(self) -> Dict[str, ProviderStatus]:
        """
        Update status of all providers
        """
        try:
            status_updates = {}
            for provider in self.providers.values():
                try:
                    is_available = await self._check_provider_health(
                        provider.name
                    )
                    status = await ProviderStatus.create(
                        provider=provider.name,
                        status='active' if is_available else 'down',
                        last_check=datetime.now(),
                        created_at=datetime.now()
                    )
                    status_updates[provider.name] = status
                except Exception as e:
                    logger.error(
                        f"Error checking {provider.name} status: {str(e)}"
                    )

            # Update active provider if needed
            await self._update_active_provider(status_updates)

            return status_updates

        except Exception as e:
            logger.error(f"Error updating provider status: {str(e)}")
            raise

    async def _geocode_with_provider(
        self,
        address: str,
        provider_name: str
    ) -> GeocodingResult:
        """
        Geocode address with specific provider
        """
        provider = self.providers[provider_name]
        
        async with aiohttp.ClientSession() as session:
            params = {
                'address': address,
                'key': provider.api_key
            }
            
            async with session.get(
                f"{provider.base_url}/geocode",
                params=params
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Geocoding request failed"
                    )

                data = await response.json()
                return self._parse_geocoding_response(data, provider_name)

    async def _get_traffic_with_provider(
        self,
        bounds: Dict[str, float],
        provider_name: str
    ) -> TrafficData:
        """
        Get traffic data from specific provider
        """
        provider = self.providers[provider_name]
        
        async with aiohttp.ClientSession() as session:
            params = {
                'bounds': f"{bounds['south']},{bounds['west']}|{bounds['north']},{bounds['east']}",
                'key': provider.api_key
            }
            
            async with session.get(
                f"{provider.base_url}/traffic",
                params=params
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Traffic data request failed"
                    )

                data = await response.json()
                return self._parse_traffic_response(data, provider_name)

    async def _check_provider_health(self, provider_name: str) -> bool:
        """
        Check health status of provider
        """
        provider = self.providers[provider_name]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{provider.base_url}/health"
                ) as response:
                    return response.status == 200
        except:
            return False

    async def _update_active_provider(
        self,
        status_updates: Dict[str, ProviderStatus]
    ) -> None:
        """
        Update active provider based on status and priority
        """
        available_providers = [
            self.providers[provider_name]
            for provider_name, status in status_updates.items()
            if status.status == 'active'
        ]

        if available_providers:
            # Sort by priority
            available_providers.sort(key=lambda x: x.priority)
            self.active_provider = available_providers[0]
            self.fallback_queue = available_providers[1:]
        else:
            logger.critical("No available map providers!")
            self.active_provider = None
            self.fallback_queue = []

    async def _create_default_style(
        self,
        style_name: str,
        provider: Optional[str] = None
    ) -> MapStyle:
        """
        Create default map style
        """
        provider_name = provider if provider else self.active_provider.name
        default_style = self.style_config.get(style_name, {})

        return await MapStyle.create(
            name=style_name,
            provider=provider_name,
            style_json=default_style,
            created_at=datetime.now()
        )

    def _parse_geocoding_response(
        self,
        response: Dict,
        provider: str
    ) -> GeocodingResult:
        """
        Parse geocoding response based on provider
        """
        if provider == 'google':
            return self._parse_google_geocoding(response)
        elif provider == 'mapbox':
            return self._parse_mapbox_geocoding(response)
        elif provider == 'here':
            return self._parse_here_geocoding(response)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _parse_traffic_response(
        self,
        response: Dict,
        provider: str
    ) -> TrafficData:
        """
        Parse traffic response based on provider
        """
        if provider == 'google':
            return self._parse_google_traffic(response)
        elif provider == 'tomtom':
            return self._parse_tomtom_traffic(response)
        elif provider == 'here':
            return self._parse_here_traffic(response)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _parse_google_geocoding(self, response: Dict) -> GeocodingResult:
        """
        Parse Google Maps geocoding response
        """
        result = response['results'][0]
        location = result['geometry']['location']
        
        return GeocodingResult(
            provider='google',
            latitude=location['lat'],
            longitude=location['lng'],
            formatted_address=result['formatted_address'],
            confidence=self._calculate_google_confidence(result),
            raw_response=result
        )

    def _parse_mapbox_geocoding(self, response: Dict) -> GeocodingResult:
        """
        Parse Mapbox geocoding response
        """
        feature = response['features'][0]
        
        return GeocodingResult(
            provider='mapbox',
            latitude=feature['center'][1],
            longitude=feature['center'][0],
            formatted_address=feature['place_name'],
            confidence=feature['relevance'],
            raw_response=feature
        )

    def _parse_here_geocoding(self, response: Dict) -> GeocodingResult:
        """
        Parse HERE Maps geocoding response
        """
        item = response['items'][0]
        position = item['position']
        
        return GeocodingResult(
            provider='here',
            latitude=position['lat'],
            longitude=position['lng'],
            formatted_address=item['address']['label'],
            confidence=self._calculate_here_confidence(item),
            raw_response=item
        )

    def _calculate_google_confidence(self, result: Dict) -> float:
        """
        Calculate confidence score for Google geocoding result
        """
        location_type = result['geometry']['location_type']
        confidence_map = {
            'ROOFTOP': 1.0,
            'RANGE_INTERPOLATED': 0.8,
            'GEOMETRIC_CENTER': 0.6,
            'APPROXIMATE': 0.4
        }
        return confidence_map.get(location_type, 0.0)

    def _calculate_here_confidence(self, item: Dict) -> float:
        """
        Calculate confidence score for HERE geocoding result
        """
        scoring = {
            'matchLevel': {
                'houseNumber': 1.0,
                'street': 0.8,
                'district': 0.6,
                'city': 0.4
            }
        }
        return scoring['matchLevel'].get(item['matchLevel'], 0.2)
