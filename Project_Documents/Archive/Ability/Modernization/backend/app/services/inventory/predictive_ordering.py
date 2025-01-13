from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd
from fastapi import HTTPException

from app.models.inventory import (
    InventoryItem,
    OrderHistory,
    SupplierPerformance,
    PurchaseOrder,
    SafetyStock
)
from app.core.config import Settings
from app.core.logging import logger
from app.services.inventory.supplier import SupplierService
from app.services.analytics.time_series import TimeSeriesAnalyzer

class PredictiveOrderingService:
    def __init__(
        self,
        settings: Settings,
        supplier_service: SupplierService,
        time_series_analyzer: TimeSeriesAnalyzer
    ):
        self.settings = settings
        self.supplier_service = supplier_service
        self.time_series_analyzer = time_series_analyzer
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )

    async def forecast_demand(
        self,
        item_id: str,
        forecast_period: int = 30
    ) -> Dict[str, float]:
        """
        Forecast demand for an item using historical data and ML
        """
        try:
            # Get historical order data
            order_history = await OrderHistory.filter(
                item_id=item_id,
                created_at__gte=datetime.now() - timedelta(days=365)
            ).order_by('created_at')

            if not order_history:
                raise HTTPException(
                    status_code=404,
                    detail=f"No order history found for item {item_id}"
                )

            # Prepare data for forecasting
            df = pd.DataFrame([{
                'date': oh.created_at,
                'quantity': oh.quantity,
                'price': oh.price,
                'promotion': oh.promotion_active,
                'season': oh.created_at.month
            } for oh in order_history])

            # Add time series features
            df = self.time_series_analyzer.add_features(df)

            # Train model
            X = df.drop(['date', 'quantity'], axis=1)
            y = df['quantity']

            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)

            # Generate future dates
            future_dates = pd.date_range(
                start=df['date'].max(),
                periods=forecast_period,
                freq='D'
            )

            # Prepare future features
            future_df = pd.DataFrame()
            future_df['date'] = future_dates
            future_df['season'] = future_dates.month
            future_df['price'] = df['price'].mean()  # Assume current price
            future_df['promotion'] = False  # Assume no promotions

            # Add time series features for future dates
            future_df = self.time_series_analyzer.add_features(future_df)
            future_X = future_df.drop(['date'], axis=1)
            future_X_scaled = self.scaler.transform(future_X)

            # Make predictions
            predictions = self.model.predict(future_X_scaled)

            return {
                str(date): float(pred)
                for date, pred in zip(future_dates, predictions)
            }

        except Exception as e:
            logger.error(f"Error forecasting demand: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error forecasting demand: {str(e)}"
            )

    async def calculate_safety_stock(
        self,
        item_id: str,
        service_level: float = 0.95
    ) -> float:
        """
        Calculate safety stock level using service level and demand variability
        """
        try:
            # Get historical demand data
            history = await OrderHistory.filter(
                item_id=item_id,
                created_at__gte=datetime.now() - timedelta(days=365)
            ).values_list('quantity', flat=True)

            if not history:
                raise HTTPException(
                    status_code=404,
                    detail=f"No order history found for item {item_id}"
                )

            # Calculate demand statistics
            demand_std = np.std(history)
            z_score = np.abs(np.percentile(np.random.standard_normal(10000), service_level * 100))

            # Get lead time from supplier performance
            supplier_perf = await SupplierPerformance.filter(
                item_id=item_id
            ).order_by('-created_at').first()

            if not supplier_perf:
                raise HTTPException(
                    status_code=404,
                    detail=f"No supplier performance data found for item {item_id}"
                )

            lead_time = supplier_perf.average_lead_time
            lead_time_std = supplier_perf.lead_time_std

            # Calculate safety stock
            safety_stock = z_score * np.sqrt(
                lead_time * demand_std**2 + 
                supplier_perf.average_daily_demand**2 * lead_time_std**2
            )

            # Save safety stock calculation
            await SafetyStock.create(
                item_id=item_id,
                level=safety_stock,
                service_level=service_level,
                calculated_at=datetime.now()
            )

            return float(safety_stock)

        except Exception as e:
            logger.error(f"Error calculating safety stock: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating safety stock: {str(e)}"
            )

    async def optimize_order_quantity(
        self,
        item_id: str,
        forecast_demand: float,
        holding_cost: float,
        ordering_cost: float
    ) -> float:
        """
        Calculate optimal order quantity using Economic Order Quantity (EOQ)
        """
        try:
            # Get item details
            item = await InventoryItem.get_or_none(id=item_id)
            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found"
                )

            # Calculate EOQ
            eoq = np.sqrt(
                (2 * forecast_demand * ordering_cost) /
                (holding_cost * item.unit_price)
            )

            return float(eoq)

        except Exception as e:
            logger.error(f"Error calculating optimal order quantity: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating optimal order quantity: {str(e)}"
            )

    async def generate_purchase_order(
        self,
        item_id: str,
        forecast_period: int = 30
    ) -> PurchaseOrder:
        """
        Generate automated purchase order based on predictions
        """
        try:
            # Get demand forecast
            demand_forecast = await self.forecast_demand(
                item_id,
                forecast_period
            )

            # Calculate total forecasted demand
            total_demand = sum(demand_forecast.values())

            # Get current inventory level
            item = await InventoryItem.get_or_none(id=item_id)
            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found"
                )

            # Calculate safety stock
            safety_stock = await self.calculate_safety_stock(item_id)

            # Get supplier performance
            supplier = await self.supplier_service.get_preferred_supplier(item_id)
            if not supplier:
                raise HTTPException(
                    status_code=404,
                    detail=f"No preferred supplier found for item {item_id}"
                )

            # Calculate optimal order quantity
            optimal_quantity = await self.optimize_order_quantity(
                item_id,
                total_demand,
                self.settings.inventory.holding_cost_rate,
                supplier.ordering_cost
            )

            # Calculate required order quantity
            required_quantity = max(
                0,
                total_demand + safety_stock - item.current_stock
            )

            # Round up to supplier's minimum order quantity
            order_quantity = max(
                supplier.minimum_order_quantity,
                np.ceil(required_quantity / supplier.minimum_order_quantity) *
                supplier.minimum_order_quantity
            )

            # Create purchase order
            po = await PurchaseOrder.create(
                item_id=item_id,
                supplier_id=supplier.id,
                quantity=order_quantity,
                unit_price=supplier.unit_price,
                expected_delivery=datetime.now() + timedelta(days=supplier.lead_time),
                status='pending',
                created_at=datetime.now(),
                forecast_demand=total_demand,
                safety_stock=safety_stock,
                optimal_quantity=optimal_quantity
            )

            return po

        except Exception as e:
            logger.error(f"Error generating purchase order: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating purchase order: {str(e)}"
            )
