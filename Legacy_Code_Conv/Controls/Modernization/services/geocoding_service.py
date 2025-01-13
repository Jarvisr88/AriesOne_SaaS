from typing import Dict, List, Optional, Tuple
import httpx
from pydantic import BaseModel
import logging
from cache.cache_service import CacheService
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeocodingResult(BaseModel):
    formatted_address: str
    latitude: float
    longitude: float
    confidence_score: float
    place_id: str
    components: Dict[str, str]

class GeocodeResponse(BaseModel):
    results: List[GeocodingResult]
    status: str

class GeocodingService:
    def __init__(self):
        self.cache = CacheService()
        self.google_api_key = "your-google-api-key"  # Move to env
        self.here_api_key = "your-here-api-key"  # Move to env
        self.cache_ttl = timedelta(days=30)

    async def geocode_address(self, address: str) -> Optional[GeocodingResult]:
        """Geocode address using multiple services with fallback"""
        cache_key = f"geocode:{address}"
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return GeocodingResult(**cached_result)

        # Try Google Maps first
        try:
            result = await self._geocode_google(address)
            if result:
                self.cache.set(cache_key, result.dict(), self.cache_ttl)
                return result
        except Exception as e:
            logger.error(f"Google geocoding failed: {e}")

        # Fallback to HERE Maps
        try:
            result = await self._geocode_here(address)
            if result:
                self.cache.set(cache_key, result.dict(), self.cache_ttl)
                return result
        except Exception as e:
            logger.error(f"HERE geocoding failed: {e}")

        return None

    async def reverse_geocode(self, lat: float, lng: float) -> Optional[GeocodingResult]:
        """Reverse geocode coordinates to address"""
        cache_key = f"reverse_geocode:{lat},{lng}"
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return GeocodingResult(**cached_result)

        # Try Google Maps first
        try:
            result = await self._reverse_geocode_google(lat, lng)
            if result:
                self.cache.set(cache_key, result.dict(), self.cache_ttl)
                return result
        except Exception as e:
            logger.error(f"Google reverse geocoding failed: {e}")

        # Fallback to HERE Maps
        try:
            result = await self._reverse_geocode_here(lat, lng)
            if result:
                self.cache.set(cache_key, result.dict(), self.cache_ttl)
                return result
        except Exception as e:
            logger.error(f"HERE reverse geocoding failed: {e}")

        return None

    async def _geocode_google(self, address: str) -> Optional[GeocodingResult]:
        """Geocode using Google Maps API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={
                        "address": address,
                        "key": self.google_api_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "OK":
                        result = data["results"][0]
                        return GeocodingResult(
                            formatted_address=result["formatted_address"],
                            latitude=result["geometry"]["location"]["lat"],
                            longitude=result["geometry"]["location"]["lng"],
                            confidence_score=self._calculate_google_confidence(result),
                            place_id=result["place_id"],
                            components=self._extract_google_components(result)
                        )
            except Exception as e:
                logger.error(f"Google Maps API error: {e}")
                return None

    async def _geocode_here(self, address: str) -> Optional[GeocodingResult]:
        """Geocode using HERE Maps API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://geocoder.ls.hereapi.com/6.2/geocode.json",
                    params={
                        "searchtext": address,
                        "apiKey": self.here_api_key,
                        "gen": "9"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "Response" in data:
                        result = data["Response"]["View"][0]["Result"][0]
                        return GeocodingResult(
                            formatted_address=result["Location"]["Address"]["Label"],
                            latitude=result["Location"]["DisplayPosition"]["Latitude"],
                            longitude=result["Location"]["DisplayPosition"]["Longitude"],
                            confidence_score=self._calculate_here_confidence(result),
                            place_id=result["Location"]["LocationId"],
                            components=self._extract_here_components(result)
                        )
            except Exception as e:
                logger.error(f"HERE Maps API error: {e}")
                return None

    def _calculate_google_confidence(self, result: Dict) -> float:
        """Calculate confidence score for Google geocoding result"""
        # Implementation would calculate confidence based on result type and precision
        return 0.9

    def _calculate_here_confidence(self, result: Dict) -> float:
        """Calculate confidence score for HERE geocoding result"""
        # Implementation would calculate confidence based on match quality
        return 0.9

    def _extract_google_components(self, result: Dict) -> Dict[str, str]:
        """Extract address components from Google result"""
        components = {}
        for component in result["address_components"]:
            for type in component["types"]:
                components[type] = component["long_name"]
        return components

    def _extract_here_components(self, result: Dict) -> Dict[str, str]:
        """Extract address components from HERE result"""
        # Implementation would extract components from HERE format
        return {}

    async def _reverse_geocode_google(self, lat: float, lng: float) -> Optional[GeocodingResult]:
        """Implementation for Google reverse geocoding"""
        pass

    async def _reverse_geocode_here(self, lat: float, lng: float) -> Optional[GeocodingResult]:
        """Implementation for HERE reverse geocoding"""
        pass

# Initialize global service
geocoding_service = GeocodingService()
