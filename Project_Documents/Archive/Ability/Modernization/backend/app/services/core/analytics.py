from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
import pandas as pd
import numpy as np
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from app.core.config import config_manager
from app.core.logging import logger
from app.core.monitoring import metrics
from app.models.core import (
    Delivery,
    Location,
    Route,
    Vehicle,
    InventoryItem,
    DeliveryStatus
)

class DeliveryAnalytics:
    """Delivery analytics service"""
    def __init__(self, db: Session):
        self.db = db
        self._setup_service()

    def _setup_service(self):
        """Setup analytics service"""
        self.analysis_window = config_manager.get("ANALYSIS_WINDOW_DAYS", 30)
        self.peak_hour_threshold = config_manager.get("PEAK_HOUR_THRESHOLD", 0.8)

    async def get_delivery_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        vehicle_id: Optional[uuid.UUID] = None
    ) -> Dict:
        """Get delivery statistics"""
        try:
            # Set date range
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=self.analysis_window)

            # Build query
            query = self.db.query(Delivery).filter(
                Delivery.created_at.between(start_date, end_date)
            )
            if vehicle_id:
                query = query.filter(Delivery.vehicle_id == vehicle_id)

            deliveries = query.all()
            
            # Calculate statistics
            total_deliveries = len(deliveries)
            completed = sum(1 for d in deliveries if d.status == DeliveryStatus.DELIVERED)
            failed = sum(1 for d in deliveries if d.status == DeliveryStatus.FAILED)
            
            completion_times = [
                (d.completed_at - d.created_at).total_seconds()
                for d in deliveries
                if d.completed_at and d.status == DeliveryStatus.DELIVERED
            ]
            
            return {
                "total_deliveries": total_deliveries,
                "completed_deliveries": completed,
                "failed_deliveries": failed,
                "completion_rate": completed / total_deliveries if total_deliveries else 0,
                "avg_completion_time": np.mean(completion_times) if completion_times else 0,
                "median_completion_time": np.median(completion_times) if completion_times else 0,
                "min_completion_time": min(completion_times) if completion_times else 0,
                "max_completion_time": max(completion_times) if completion_times else 0
            }
            
        except Exception as e:
            logger.error(f"Delivery stats error: {e}")
            raise

    async def analyze_routes(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Analyze delivery routes"""
        try:
            # Set date range
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=self.analysis_window)

            # Get routes
            routes = self.db.query(Route).join(Delivery).filter(
                Delivery.created_at.between(start_date, end_date)
            ).all()
            
            # Calculate metrics
            distances = [r.distance for r in routes if r.distance]
            durations = [r.duration for r in routes if r.duration]
            
            return {
                "total_routes": len(routes),
                "total_distance": sum(distances),
                "avg_distance": np.mean(distances) if distances else 0,
                "avg_duration": np.mean(durations) if durations else 0,
                "distance_histogram": np.histogram(distances, bins=10)[0].tolist() if distances else [],
                "duration_histogram": np.histogram(durations, bins=10)[0].tolist() if durations else []
            }
            
        except Exception as e:
            logger.error(f"Route analysis error: {e}")
            raise

    async def identify_peak_hours(
        self,
        days: int = 7
    ) -> Dict:
        """Identify peak delivery hours"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get deliveries
            deliveries = self.db.query(Delivery).filter(
                Delivery.created_at >= start_date
            ).all()
            
            # Create hourly distribution
            hours = [d.created_at.hour for d in deliveries]
            distribution = pd.Series(hours).value_counts().sort_index()
            max_deliveries = distribution.max()
            
            # Identify peak hours
            peak_hours = distribution[
                distribution >= max_deliveries * self.peak_hour_threshold
            ].index.tolist()
            
            return {
                "peak_hours": peak_hours,
                "hourly_distribution": distribution.to_dict(),
                "max_deliveries_per_hour": max_deliveries
            }
            
        except Exception as e:
            logger.error(f"Peak hours analysis error: {e}")
            raise

    async def analyze_inventory_trends(
        self,
        days: int = 30
    ) -> Dict:
        """Analyze inventory trends"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get deliveries with items
            deliveries = self.db.query(Delivery).filter(
                and_(
                    Delivery.created_at >= start_date,
                    Delivery.status == DeliveryStatus.DELIVERED
                )
            ).all()
            
            # Analyze item usage
            item_usage = {}
            for delivery in deliveries:
                for item in delivery.items:
                    item_id = item["item_id"]
                    quantity = item["quantity"]
                    if item_id in item_usage:
                        item_usage[item_id] += quantity
                    else:
                        item_usage[item_id] = quantity
            
            # Get item details
            items = self.db.query(InventoryItem).filter(
                InventoryItem.id.in_(item_usage.keys())
            ).all()
            
            return {
                "most_delivered_items": [
                    {
                        "item_id": str(item.id),
                        "name": item.name,
                        "quantity": item_usage[str(item.id)],
                        "current_stock": item.quantity
                    }
                    for item in sorted(
                        items,
                        key=lambda x: item_usage[str(x.id)],
                        reverse=True
                    )[:10]
                ],
                "low_stock_items": [
                    {
                        "item_id": str(item.id),
                        "name": item.name,
                        "current_stock": item.quantity,
                        "usage_rate": item_usage.get(str(item.id), 0) / days
                    }
                    for item in items
                    if item.quantity < item_usage.get(str(item.id), 0) / days * 7  # Less than 7 days of stock
                ]
            }
            
        except Exception as e:
            logger.error(f"Inventory analysis error: {e}")
            raise

    async def generate_vehicle_insights(
        self,
        days: int = 30
    ) -> Dict:
        """Generate vehicle performance insights"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get vehicles and their deliveries
            vehicles = self.db.query(Vehicle).all()
            vehicle_stats = []
            
            for vehicle in vehicles:
                deliveries = self.db.query(Delivery).filter(
                    and_(
                        Delivery.vehicle_id == vehicle.id,
                        Delivery.created_at >= start_date
                    )
                ).all()
                
                # Calculate metrics
                total_deliveries = len(deliveries)
                completed = sum(1 for d in deliveries if d.status == DeliveryStatus.DELIVERED)
                total_distance = sum(
                    d.route.distance
                    for d in deliveries
                    if d.route and d.route.distance
                )
                
                vehicle_stats.append({
                    "vehicle_id": str(vehicle.id),
                    "name": vehicle.name,
                    "type": vehicle.type,
                    "total_deliveries": total_deliveries,
                    "completed_deliveries": completed,
                    "completion_rate": completed / total_deliveries if total_deliveries else 0,
                    "total_distance": total_distance,
                    "avg_distance_per_delivery": total_distance / completed if completed else 0
                })
            
            return {
                "vehicle_stats": vehicle_stats,
                "best_performers": sorted(
                    vehicle_stats,
                    key=lambda x: x["completion_rate"],
                    reverse=True
                )[:3],
                "most_active": sorted(
                    vehicle_stats,
                    key=lambda x: x["total_deliveries"],
                    reverse=True
                )[:3]
            }
            
        except Exception as e:
            logger.error(f"Vehicle analysis error: {e}")
            raise

    async def predict_delivery_time(
        self,
        delivery_id: uuid.UUID
    ) -> Dict:
        """Predict delivery completion time"""
        try:
            delivery = self.db.query(Delivery).get(delivery_id)
            if not delivery:
                raise ValueError("Delivery not found")
                
            # Get historical data
            similar_deliveries = self.db.query(Delivery).filter(
                and_(
                    Delivery.status == DeliveryStatus.DELIVERED,
                    Delivery.id != delivery_id
                )
            ).all()
            
            # Calculate features
            distance = delivery.route.distance if delivery.route else 0
            item_count = sum(item["quantity"] for item in delivery.items)
            
            # Build prediction model
            completion_times = []
            for d in similar_deliveries:
                if d.completed_at and d.route:
                    features = {
                        "distance": d.route.distance,
                        "item_count": sum(item["quantity"] for item in d.items)
                    }
                    completion_time = (d.completed_at - d.created_at).total_seconds()
                    completion_times.append((features, completion_time))
            
            if not completion_times:
                return {
                    "estimated_time": None,
                    "confidence": 0,
                    "similar_deliveries": 0
                }
            
            # Simple prediction based on similar deliveries
            similar = [
                ct for f, ct in completion_times
                if abs(f["distance"] - distance) / distance < 0.2
                and abs(f["item_count"] - item_count) / item_count < 0.2
            ]
            
            if similar:
                estimate = np.mean(similar)
                confidence = 1.0 - np.std(similar) / estimate
            else:
                estimate = np.mean([ct for _, ct in completion_times])
                confidence = 0.5
            
            return {
                "estimated_time": estimate,
                "confidence": confidence,
                "similar_deliveries": len(similar)
            }
            
        except Exception as e:
            logger.error(f"Delivery prediction error: {e}")
            raise

# Create analytics service factory
def get_delivery_analytics(db: Session) -> DeliveryAnalytics:
    return DeliveryAnalytics(db)
