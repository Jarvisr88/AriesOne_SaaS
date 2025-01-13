from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp
import asyncio
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.weather import (
    WeatherData,
    WeatherForecast,
    WeatherAlert,
    WeatherImpact,
    WeatherProvider
)

class WeatherService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.providers = self._initialize_providers()
        self.cache = {}
        self.alert_subscribers = set()

    def _initialize_providers(self) -> Dict[str, WeatherProvider]:
        """
        Initialize weather data providers
        """
        providers = {}
        for provider_config in self.settings.weather.providers:
            providers[provider_config.name] = WeatherProvider(
                name=provider_config.name,
                api_key=provider_config.api_key,
                base_url=provider_config.base_url,
                priority=provider_config.priority
            )
        return providers

    async def get_current_weather(
        self,
        location: Dict[str, float],
        provider: Optional[str] = None
    ) -> WeatherData:
        """
        Get real-time weather data
        """
        try:
            if provider:
                return await self._get_weather_with_provider(
                    location,
                    provider
                )

            # Try providers in priority order
            for provider in sorted(
                self.providers.values(),
                key=lambda x: x.priority
            ):
                try:
                    return await self._get_weather_with_provider(
                        location,
                        provider.name
                    )
                except Exception as e:
                    logger.warning(
                        f"Weather data failed with {provider.name}: {str(e)}"
                    )
                    continue

            raise HTTPException(
                status_code=500,
                detail="All weather providers failed"
            )

        except Exception as e:
            logger.error(f"Error getting weather data: {str(e)}")
            raise

    async def get_weather_forecast(
        self,
        location: Dict[str, float],
        days: int = 5,
        provider: Optional[str] = None
    ) -> List[WeatherForecast]:
        """
        Get weather forecast
        """
        try:
            if provider:
                return await self._get_forecast_with_provider(
                    location,
                    days,
                    provider
                )

            # Try providers in priority order
            for provider in sorted(
                self.providers.values(),
                key=lambda x: x.priority
            ):
                try:
                    return await self._get_forecast_with_provider(
                        location,
                        days,
                        provider.name
                    )
                except Exception as e:
                    logger.warning(
                        f"Forecast failed with {provider.name}: {str(e)}"
                    )
                    continue

            raise HTTPException(
                status_code=500,
                detail="All forecast providers failed"
            )

        except Exception as e:
            logger.error(f"Error getting forecast: {str(e)}")
            raise

    async def get_weather_alerts(
        self,
        location: Dict[str, float],
        provider: Optional[str] = None
    ) -> List[WeatherAlert]:
        """
        Get severe weather alerts
        """
        try:
            if provider:
                return await self._get_alerts_with_provider(
                    location,
                    provider
                )

            # Try providers in priority order
            alerts = []
            for provider in sorted(
                self.providers.values(),
                key=lambda x: x.priority
            ):
                try:
                    provider_alerts = await self._get_alerts_with_provider(
                        location,
                        provider.name
                    )
                    alerts.extend(provider_alerts)
                except Exception as e:
                    logger.warning(
                        f"Alerts failed with {provider.name}: {str(e)}"
                    )
                    continue

            return self._deduplicate_alerts(alerts)

        except Exception as e:
            logger.error(f"Error getting weather alerts: {str(e)}")
            raise

    async def analyze_weather_impact(
        self,
        route: Dict,
        schedule: datetime
    ) -> WeatherImpact:
        """
        Analyze weather impact on delivery
        """
        try:
            # Get weather data along route
            route_weather = await self._get_route_weather(route, schedule)

            # Analyze severe conditions
            severe_conditions = self._identify_severe_conditions(route_weather)

            # Calculate delay probability
            delay_probability = self._calculate_delay_probability(
                route_weather,
                severe_conditions
            )

            # Generate recommendations
            recommendations = self._generate_weather_recommendations(
                severe_conditions,
                delay_probability
            )

            # Create impact record
            impact = await WeatherImpact.create(
                route_id=route['id'],
                schedule_time=schedule,
                weather_conditions=route_weather,
                severe_conditions=severe_conditions,
                delay_probability=delay_probability,
                recommendations=recommendations,
                created_at=datetime.now()
            )

            return impact

        except Exception as e:
            logger.error(f"Error analyzing weather impact: {str(e)}")
            raise

    async def subscribe_to_alerts(
        self,
        location: Dict[str, float],
        callback: callable
    ) -> None:
        """
        Subscribe to weather alerts
        """
        self.alert_subscribers.add((location, callback))

    async def unsubscribe_from_alerts(
        self,
        location: Dict[str, float],
        callback: callable
    ) -> None:
        """
        Unsubscribe from weather alerts
        """
        self.alert_subscribers.discard((location, callback))

    async def _get_weather_with_provider(
        self,
        location: Dict[str, float],
        provider_name: str
    ) -> WeatherData:
        """
        Get weather data from specific provider
        """
        provider = self.providers[provider_name]
        
        async with aiohttp.ClientSession() as session:
            params = {
                'lat': location['latitude'],
                'lon': location['longitude'],
                'key': provider.api_key
            }
            
            async with session.get(
                f"{provider.base_url}/current",
                params=params
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Weather request failed"
                    )

                data = await response.json()
                return self._parse_weather_response(data, provider_name)

    async def _get_forecast_with_provider(
        self,
        location: Dict[str, float],
        days: int,
        provider_name: str
    ) -> List[WeatherForecast]:
        """
        Get forecast from specific provider
        """
        provider = self.providers[provider_name]
        
        async with aiohttp.ClientSession() as session:
            params = {
                'lat': location['latitude'],
                'lon': location['longitude'],
                'days': days,
                'key': provider.api_key
            }
            
            async with session.get(
                f"{provider.base_url}/forecast",
                params=params
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Forecast request failed"
                    )

                data = await response.json()
                return self._parse_forecast_response(data, provider_name)

    async def _get_alerts_with_provider(
        self,
        location: Dict[str, float],
        provider_name: str
    ) -> List[WeatherAlert]:
        """
        Get alerts from specific provider
        """
        provider = self.providers[provider_name]
        
        async with aiohttp.ClientSession() as session:
            params = {
                'lat': location['latitude'],
                'lon': location['longitude'],
                'key': provider.api_key
            }
            
            async with session.get(
                f"{provider.base_url}/alerts",
                params=params
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Alerts request failed"
                    )

                data = await response.json()
                return self._parse_alerts_response(data, provider_name)

    async def _get_route_weather(
        self,
        route: Dict,
        schedule: datetime
    ) -> List[Dict]:
        """
        Get weather data along route
        """
        weather_data = []
        for point in route['points']:
            weather = await self.get_current_weather({
                'latitude': point['lat'],
                'longitude': point['lng']
            })
            weather_data.append({
                'point': point,
                'weather': weather
            })
        return weather_data

    def _identify_severe_conditions(
        self,
        route_weather: List[Dict]
    ) -> List[Dict]:
        """
        Identify severe weather conditions
        """
        severe_conditions = []
        for point in route_weather:
            conditions = self._check_severe_conditions(point['weather'])
            if conditions:
                severe_conditions.append({
                    'point': point['point'],
                    'conditions': conditions
                })
        return severe_conditions

    def _calculate_delay_probability(
        self,
        route_weather: List[Dict],
        severe_conditions: List[Dict]
    ) -> float:
        """
        Calculate probability of weather-related delays
        """
        base_probability = 0.0
        
        # Factor in severe conditions
        if severe_conditions:
            base_probability += len(severe_conditions) * 0.2

        # Factor in general weather conditions
        for point in route_weather:
            base_probability += self._get_condition_factor(
                point['weather']
            )

        return min(base_probability, 1.0)

    def _generate_weather_recommendations(
        self,
        severe_conditions: List[Dict],
        delay_probability: float
    ) -> List[str]:
        """
        Generate weather-based recommendations
        """
        recommendations = []

        if delay_probability > 0.7:
            recommendations.append("Consider rescheduling delivery")
        elif delay_probability > 0.4:
            recommendations.append("Allow extra time for delivery")

        for condition in severe_conditions:
            recommendations.extend(
                self._get_condition_recommendations(condition)
            )

        return recommendations

    def _check_severe_conditions(self, weather: WeatherData) -> List[str]:
        """
        Check for severe weather conditions
        """
        severe = []
        if weather.wind_speed > 50:  # km/h
            severe.append('high_winds')
        if weather.precipitation > 25:  # mm/h
            severe.append('heavy_rain')
        if weather.visibility < 1:  # km
            severe.append('low_visibility')
        if weather.temperature < -10:  # Celsius
            severe.append('extreme_cold')
        if weather.temperature > 40:  # Celsius
            severe.append('extreme_heat')
        return severe

    def _get_condition_factor(self, weather: WeatherData) -> float:
        """
        Get delay probability factor for weather condition
        """
        factors = {
            'rain': 0.1,
            'snow': 0.3,
            'fog': 0.2,
            'wind': 0.1,
            'storm': 0.4
        }
        return factors.get(weather.condition, 0.0)

    def _get_condition_recommendations(
        self,
        condition: Dict
    ) -> List[str]:
        """
        Get recommendations for specific conditions
        """
        recommendations = {
            'high_winds': [
                "Use caution with high-profile vehicles",
                "Watch for debris on roads"
            ],
            'heavy_rain': [
                "Reduce speed",
                "Maintain safe following distance"
            ],
            'low_visibility': [
                "Use headlights",
                "Reduce speed significantly"
            ],
            'extreme_cold': [
                "Check vehicle systems",
                "Carry emergency supplies"
            ],
            'extreme_heat': [
                "Monitor vehicle temperature",
                "Carry extra water"
            ]
        }
        return recommendations.get(condition['conditions'][0], [])
