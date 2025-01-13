from datetime import datetime, timedelta
from typing import Dict, List
import aiohttp
from fastapi import HTTPException

from app.core.config import Settings
from app.core.logging import logger

class WeatherService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.weather_api.key
        self.base_url = settings.weather_api.url

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> Dict[str, List[float]]:
        """
        Get weather forecast for a location
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'api_key': self.api_key,
                    'lat': latitude,
                    'lon': longitude,
                    'days': days,
                }
                
                async with session.get(
                    f"{self.base_url}/forecast",
                    params=params
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="Error fetching weather forecast"
                        )
                    
                    data = await response.json()
                    
                    # Extract relevant weather features
                    forecast = {
                        'temperature': [],
                        'precipitation': [],
                        'humidity': [],
                        'wind_speed': [],
                        'cloud_cover': []
                    }
                    
                    for day in data['daily']:
                        forecast['temperature'].append(day['temp']['day'])
                        forecast['precipitation'].append(day['pop'])
                        forecast['humidity'].append(day['humidity'])
                        forecast['wind_speed'].append(day['wind_speed'])
                        forecast['cloud_cover'].append(day['clouds'])
                    
                    return forecast

        except Exception as e:
            logger.error(f"Error fetching weather forecast: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching weather forecast: {str(e)}"
            )

    async def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, List[float]]:
        """
        Get historical weather data for a location
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'api_key': self.api_key,
                    'lat': latitude,
                    'lon': longitude,
                    'start': int(start_date.timestamp()),
                    'end': int(end_date.timestamp()),
                }
                
                async with session.get(
                    f"{self.base_url}/history",
                    params=params
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="Error fetching historical weather"
                        )
                    
                    data = await response.json()
                    
                    # Extract historical weather data
                    history = {
                        'temperature': [],
                        'precipitation': [],
                        'humidity': [],
                        'wind_speed': [],
                        'cloud_cover': []
                    }
                    
                    for day in data['daily']:
                        history['temperature'].append(day['temp']['day'])
                        history['precipitation'].append(day['pop'])
                        history['humidity'].append(day['humidity'])
                        history['wind_speed'].append(day['wind_speed'])
                        history['cloud_cover'].append(day['clouds'])
                    
                    return history

        except Exception as e:
            logger.error(f"Error fetching historical weather: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching historical weather: {str(e)}"
            )

    async def analyze_weather_impact(
        self,
        latitude: float,
        longitude: float,
        sales_data: List[Dict]
    ) -> Dict:
        """
        Analyze correlation between weather and sales
        """
        try:
            # Get weather data for sales period
            start_date = min(sale['date'] for sale in sales_data)
            end_date = max(sale['date'] for sale in sales_data)
            
            weather_data = await self.get_historical_weather(
                latitude,
                longitude,
                start_date,
                end_date
            )
            
            # Calculate correlations
            correlations = {}
            for weather_factor in weather_data:
                correlation = np.corrcoef(
                    [sale['quantity'] for sale in sales_data],
                    weather_data[weather_factor]
                )[0, 1]
                correlations[weather_factor] = float(correlation)
            
            # Determine significant weather factors
            significant_factors = {
                factor: corr
                for factor, corr in correlations.items()
                if abs(corr) > 0.3  # Correlation threshold
            }
            
            return {
                'correlations': correlations,
                'significant_factors': significant_factors,
                'sample_size': len(sales_data)
            }

        except Exception as e:
            logger.error(f"Error analyzing weather impact: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing weather impact: {str(e)}"
            )
