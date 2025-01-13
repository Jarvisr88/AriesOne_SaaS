from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from prophet import Prophet
from fastapi import HTTPException

from app.models.inventory import (
    InventoryItem,
    SalesHistory,
    MarketTrend,
    ProductLifecycle,
    LocationInventory,
    PromotionEvent,
    CompetitorPrice,
    ForecastResult
)
from app.core.config import Settings
from app.core.logging import logger
from app.services.analytics.time_series import TimeSeriesAnalyzer
from app.services.external.weather import WeatherService
from app.services.external.market import MarketDataService

class InventoryForecastingService:
    def __init__(
        self,
        settings: Settings,
        time_series_analyzer: TimeSeriesAnalyzer,
        weather_service: WeatherService,
        market_service: MarketDataService
    ):
        self.settings = settings
        self.time_series_analyzer = time_series_analyzer
        self.weather_service = weather_service
        self.market_service = market_service
        self.scaler = StandardScaler()
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )

    async def analyze_historical_data(
        self,
        item_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Analyze historical sales data with multiple factors
        """
        try:
            # Get sales history
            sales_data = await SalesHistory.filter(
                item_id=item_id,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')

            if not sales_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"No sales history found for item {item_id}"
                )

            # Create base dataframe
            df = pd.DataFrame([{
                'date': sale.date,
                'quantity': sale.quantity,
                'revenue': sale.revenue,
                'location_id': sale.location_id
            } for sale in sales_data])

            # Add time series features
            df = self.time_series_analyzer.add_features(df)

            # Add market trends
            market_trends = await MarketTrend.filter(
                item_id=item_id,
                date__gte=start_date,
                date__lte=end_date
            )
            market_df = pd.DataFrame([{
                'date': trend.date,
                'market_demand': trend.demand_index,
                'market_price': trend.average_price
            } for trend in market_trends])
            df = df.merge(market_df, on='date', how='left')

            # Analyze patterns
            analysis = {
                'total_sales': float(df['quantity'].sum()),
                'average_daily_sales': float(df['quantity'].mean()),
                'sales_growth': float(
                    (df['quantity'].iloc[-30:].mean() / 
                     df['quantity'].iloc[:30].mean() - 1) * 100
                ),
                'seasonality': self.time_series_analyzer.detect_seasonality(
                    df['quantity'].values
                ),
                'trends': self.time_series_analyzer.analyze_trends(
                    df['quantity'].values
                )
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing historical data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing historical data: {str(e)}"
            )

    async def integrate_market_trends(
        self,
        item_id: str,
        forecast_date: datetime
    ) -> Dict:
        """
        Integrate market trends and competition analysis
        """
        try:
            # Get market data
            market_data = await self.market_service.get_market_data(
                item_id,
                forecast_date
            )

            # Get competitor prices
            competitor_prices = await CompetitorPrice.filter(
                item_id=item_id,
                date=forecast_date
            )

            # Analyze market position
            total_market_size = market_data['market_size']
            competitor_data = [{
                'competitor': price.competitor_name,
                'price': price.price,
                'market_share': price.market_share
            } for price in competitor_prices]

            # Calculate market metrics
            market_analysis = {
                'market_size': total_market_size,
                'market_growth': market_data['growth_rate'],
                'market_share': market_data['our_market_share'],
                'price_position': {
                    'our_price': market_data['our_price'],
                    'market_average': market_data['average_price'],
                    'price_index': market_data['our_price'] / market_data['average_price']
                },
                'competitors': competitor_data
            }

            return market_analysis

        except Exception as e:
            logger.error(f"Error integrating market trends: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error integrating market trends: {str(e)}"
            )

    async def analyze_product_lifecycle(
        self,
        item_id: str
    ) -> Dict:
        """
        Analyze product lifecycle stage and impact
        """
        try:
            lifecycle = await ProductLifecycle.get_or_none(item_id=item_id)
            if not lifecycle:
                raise HTTPException(
                    status_code=404,
                    detail=f"No lifecycle data found for item {item_id}"
                )

            # Calculate lifecycle metrics
            total_duration = (datetime.now() - lifecycle.launch_date).days
            stage_duration = (datetime.now() - lifecycle.stage_start_date).days

            analysis = {
                'current_stage': lifecycle.current_stage,
                'stage_duration': stage_duration,
                'total_duration': total_duration,
                'stage_progress': stage_duration / lifecycle.expected_stage_duration,
                'growth_rate': lifecycle.growth_rate,
                'market_penetration': lifecycle.market_penetration,
                'expected_remaining_duration': lifecycle.expected_remaining_duration
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing product lifecycle: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing product lifecycle: {str(e)}"
            )

    async def forecast_by_location(
        self,
        item_id: str,
        location_ids: List[str],
        forecast_days: int = 30
    ) -> Dict[str, Dict]:
        """
        Generate forecasts for multiple locations
        """
        try:
            location_forecasts = {}
            
            for location_id in location_ids:
                # Get location-specific data
                location_sales = await SalesHistory.filter(
                    item_id=item_id,
                    location_id=location_id
                ).order_by('date')

                if not location_sales:
                    continue

                # Create Prophet model for location
                df = pd.DataFrame([{
                    'ds': sale.date,
                    'y': sale.quantity
                } for sale in location_sales])

                model = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=True,
                    daily_seasonality=True
                )

                # Add location-specific features
                location = await LocationInventory.get(id=location_id)
                if location.weather_sensitive:
                    weather_data = await self.weather_service.get_forecast(
                        location.latitude,
                        location.longitude,
                        forecast_days
                    )
                    for condition in weather_data:
                        model.add_regressor(condition)
                        df[condition] = weather_data[condition]

                # Fit model and make forecast
                model.fit(df)
                future = model.make_future_dataframe(periods=forecast_days)
                forecast = model.predict(future)

                location_forecasts[location_id] = {
                    'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
                    .tail(forecast_days)
                    .to_dict('records'),
                    'location_factors': {
                        'weather_impact': location.weather_sensitive,
                        'local_events': location.local_events,
                        'demographics': location.demographic_factors
                    }
                }

            return location_forecasts

        except Exception as e:
            logger.error(f"Error forecasting by location: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error forecasting by location: {str(e)}"
            )

    async def analyze_promotion_impact(
        self,
        item_id: str,
        promotion_id: str
    ) -> Dict:
        """
        Analyze impact of promotions on demand
        """
        try:
            promotion = await PromotionEvent.get_or_none(id=promotion_id)
            if not promotion:
                raise HTTPException(
                    status_code=404,
                    detail=f"Promotion {promotion_id} not found"
                )

            # Get sales during promotion
            promotion_sales = await SalesHistory.filter(
                item_id=item_id,
                date__gte=promotion.start_date,
                date__lte=promotion.end_date
            )

            # Get baseline sales (same duration before promotion)
            baseline_start = promotion.start_date - timedelta(
                days=(promotion.end_date - promotion.start_date).days
            )
            baseline_sales = await SalesHistory.filter(
                item_id=item_id,
                date__gte=baseline_start,
                date__lt=promotion.start_date
            )

            # Calculate impact metrics
            promotion_daily_sales = sum(s.quantity for s in promotion_sales) / len(promotion_sales)
            baseline_daily_sales = sum(s.quantity for s in baseline_sales) / len(baseline_sales)
            
            impact = {
                'lift_percentage': (
                    (promotion_daily_sales / baseline_daily_sales - 1) * 100
                    if baseline_daily_sales > 0 else 0
                ),
                'additional_units': sum(s.quantity for s in promotion_sales) - 
                                  sum(s.quantity for s in baseline_sales),
                'revenue_impact': sum(s.revenue for s in promotion_sales) -
                                sum(s.revenue for s in baseline_sales),
                'promotion_details': {
                    'type': promotion.promotion_type,
                    'discount': promotion.discount_percentage,
                    'duration': (promotion.end_date - promotion.start_date).days
                }
            }

            return impact

        except Exception as e:
            logger.error(f"Error analyzing promotion impact: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing promotion impact: {str(e)}"
            )

    async def generate_forecast(
        self,
        item_id: str,
        forecast_days: int = 30
    ) -> ForecastResult:
        """
        Generate comprehensive forecast combining all factors
        """
        try:
            # Get all required data
            historical = await self.analyze_historical_data(
                item_id,
                datetime.now() - timedelta(days=365),
                datetime.now()
            )
            market = await self.integrate_market_trends(
                item_id,
                datetime.now()
            )
            lifecycle = await self.analyze_product_lifecycle(item_id)
            locations = await self.forecast_by_location(
                item_id,
                [loc.id for loc in await LocationInventory.all()],
                forecast_days
            )

            # Combine forecasts and create result
            forecast = await ForecastResult.create(
                item_id=item_id,
                forecast_date=datetime.now(),
                forecast_days=forecast_days,
                historical_analysis=historical,
                market_analysis=market,
                lifecycle_analysis=lifecycle,
                location_forecasts=locations,
                confidence_level=0.95,
                created_at=datetime.now()
            )

            return forecast

        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating forecast: {str(e)}"
            )
