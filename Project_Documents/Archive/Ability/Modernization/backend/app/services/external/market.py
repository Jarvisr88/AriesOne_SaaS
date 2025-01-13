from datetime import datetime
from typing import Dict, Optional
import aiohttp
from fastapi import HTTPException

from app.core.config import Settings
from app.core.logging import logger

class MarketDataService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.market_api.key
        self.base_url = settings.market_api.url

    async def get_market_data(
        self,
        item_id: str,
        date: datetime
    ) -> Dict:
        """
        Get market data from external API
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'api_key': self.api_key,
                    'item_id': item_id,
                    'date': date.isoformat(),
                }
                
                async with session.get(
                    f"{self.base_url}/market-data",
                    params=params
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="Error fetching market data"
                        )
                    
                    data = await response.json()
                    
                    return {
                        'market_size': data['market_size'],
                        'growth_rate': data['growth_rate'],
                        'our_market_share': data['market_share'],
                        'our_price': data['price'],
                        'average_price': data['average_price'],
                        'competitor_data': data['competitors']
                    }

        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching market data: {str(e)}"
            )

    async def get_competitor_prices(
        self,
        item_id: str,
        date: datetime
    ) -> Dict:
        """
        Get competitor pricing data
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'api_key': self.api_key,
                    'item_id': item_id,
                    'date': date.isoformat(),
                }
                
                async with session.get(
                    f"{self.base_url}/competitor-prices",
                    params=params
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="Error fetching competitor prices"
                        )
                    
                    data = await response.json()
                    
                    return {
                        'competitors': data['competitors'],
                        'average_price': data['average_price'],
                        'price_range': data['price_range'],
                        'market_leader': data['market_leader']
                    }

        except Exception as e:
            logger.error(f"Error fetching competitor prices: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching competitor prices: {str(e)}"
            )

    async def get_market_trends(
        self,
        category: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Get market trends for a category
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'api_key': self.api_key,
                    'category': category,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                }
                
                async with session.get(
                    f"{self.base_url}/market-trends",
                    params=params
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail="Error fetching market trends"
                        )
                    
                    data = await response.json()
                    
                    return {
                        'trends': data['trends'],
                        'growth_factors': data['growth_factors'],
                        'consumer_sentiment': data['consumer_sentiment'],
                        'category_performance': data['category_performance']
                    }

        except Exception as e:
            logger.error(f"Error fetching market trends: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching market trends: {str(e)}"
            )
