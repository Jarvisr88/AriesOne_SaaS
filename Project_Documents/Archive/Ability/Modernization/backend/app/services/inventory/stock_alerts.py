from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
import asyncio
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.services.notifications import NotificationService
from app.services.inventory.predictive_ordering import PredictiveOrderingService

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    LOW_STOCK = "low_stock"
    OVERSTOCK = "overstock"
    EXPIRING = "expiring"
    STOCKOUT = "stockout"
    REORDER = "reorder"

class StockAlertService:
    def __init__(
        self,
        settings: Settings,
        notification_service: NotificationService,
        predictive_ordering: PredictiveOrderingService
    ):
        self.settings = settings
        self.notification_service = notification_service
        self.predictive_ordering = predictive_ordering
        self.alert_thresholds = settings.inventory.alert_thresholds
        self.check_interval = settings.inventory.check_interval

    async def monitor_inventory_levels(self):
        """
        Continuous inventory monitoring
        """
        while True:
            try:
                # Get all inventory items
                items = await InventoryItem.all().prefetch_related(
                    'location_inventory',
                    'expiration_dates'
                )

                for item in items:
                    # Check stock levels
                    await self.check_stock_levels(item)
                    
                    # Check expiration dates
                    await self.check_expiration_dates(item)
                    
                    # Check overstock conditions
                    await self.check_overstock(item)

                # Wait for next check interval
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error monitoring inventory: {str(e)}")
                await asyncio.sleep(60)  # Wait before retry

    async def check_stock_levels(self, item: 'InventoryItem'):
        """
        Check item stock levels across locations
        """
        try:
            total_stock = 0
            location_alerts = []

            for location in item.location_inventory:
                current_stock = location.current_stock
                threshold = location.alert_threshold or item.default_threshold

                # Check location-specific stock level
                if current_stock <= 0:
                    await self.create_alert(
                        item_id=item.id,
                        location_id=location.id,
                        alert_type=AlertType.STOCKOUT,
                        priority=AlertPriority.CRITICAL,
                        message=f"Stockout at {location.name}",
                        current_value=current_stock,
                        threshold_value=threshold
                    )
                elif current_stock <= threshold:
                    priority = self.calculate_priority(
                        current_stock,
                        threshold,
                        item.lead_time
                    )
                    await self.create_alert(
                        item_id=item.id,
                        location_id=location.id,
                        alert_type=AlertType.LOW_STOCK,
                        priority=priority,
                        message=f"Low stock at {location.name}",
                        current_value=current_stock,
                        threshold_value=threshold
                    )

                total_stock += current_stock

            # Check if reorder needed
            if total_stock <= item.reorder_point:
                await self.handle_reorder(item)

        except Exception as e:
            logger.error(f"Error checking stock levels: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error checking stock levels: {str(e)}"
            )

    async def check_expiration_dates(self, item: 'InventoryItem'):
        """
        Check item expiration dates
        """
        try:
            now = datetime.now()
            expiration_window = timedelta(days=self.settings.inventory.expiration_alert_days)

            for batch in item.expiration_dates:
                if batch.expiration_date and batch.quantity > 0:
                    days_until_expiry = (batch.expiration_date - now).days

                    if days_until_expiry <= 0:
                        await self.create_alert(
                            item_id=item.id,
                            location_id=batch.location_id,
                            alert_type=AlertType.EXPIRING,
                            priority=AlertPriority.CRITICAL,
                            message=f"Expired stock: {batch.quantity} units",
                            current_value=days_until_expiry,
                            threshold_value=0,
                            metadata={
                                'batch_number': batch.batch_number,
                                'expiry_date': batch.expiration_date.isoformat()
                            }
                        )
                    elif days_until_expiry <= self.settings.inventory.expiration_alert_days:
                        priority = self.calculate_expiry_priority(days_until_expiry)
                        await self.create_alert(
                            item_id=item.id,
                            location_id=batch.location_id,
                            alert_type=AlertType.EXPIRING,
                            priority=priority,
                            message=f"Stock expiring in {days_until_expiry} days",
                            current_value=days_until_expiry,
                            threshold_value=self.settings.inventory.expiration_alert_days,
                            metadata={
                                'batch_number': batch.batch_number,
                                'expiry_date': batch.expiration_date.isoformat()
                            }
                        )

        except Exception as e:
            logger.error(f"Error checking expiration dates: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error checking expiration dates: {str(e)}"
            )

    async def check_overstock(self, item: 'InventoryItem'):
        """
        Check for overstock conditions
        """
        try:
            for location in item.location_inventory:
                max_stock = location.max_stock or item.default_max_stock
                current_stock = location.current_stock

                if current_stock > max_stock:
                    excess_percentage = ((current_stock - max_stock) / max_stock) * 100
                    priority = self.calculate_overstock_priority(excess_percentage)

                    await self.create_alert(
                        item_id=item.id,
                        location_id=location.id,
                        alert_type=AlertType.OVERSTOCK,
                        priority=priority,
                        message=f"Overstock: {excess_percentage:.1f}% above maximum",
                        current_value=current_stock,
                        threshold_value=max_stock,
                        metadata={
                            'excess_units': current_stock - max_stock,
                            'excess_percentage': excess_percentage
                        }
                    )

        except Exception as e:
            logger.error(f"Error checking overstock: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error checking overstock: {str(e)}"
            )

    async def handle_reorder(self, item: 'InventoryItem'):
        """
        Handle automated reordering
        """
        try:
            # Check if auto-reorder is enabled
            if not item.auto_reorder:
                return

            # Check if there's already a pending order
            existing_order = await PurchaseOrder.filter(
                item_id=item.id,
                status__in=['pending', 'approved']
            ).first()

            if existing_order:
                return

            # Generate purchase order
            purchase_order = await self.predictive_ordering.generate_purchase_order(
                item.id
            )

            await self.create_alert(
                item_id=item.id,
                alert_type=AlertType.REORDER,
                priority=AlertPriority.HIGH,
                message=f"Auto-reorder initiated: PO #{purchase_order.id}",
                current_value=item.current_stock,
                threshold_value=item.reorder_point,
                metadata={
                    'purchase_order_id': str(purchase_order.id),
                    'quantity': purchase_order.quantity,
                    'expected_delivery': purchase_order.expected_delivery.isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Error handling reorder: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error handling reorder: {str(e)}"
            )

    async def create_alert(
        self,
        item_id: str,
        alert_type: AlertType,
        priority: AlertPriority,
        message: str,
        current_value: float,
        threshold_value: float,
        location_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Create and send alert
        """
        try:
            # Create alert record
            alert = await StockAlert.create(
                item_id=item_id,
                location_id=location_id,
                alert_type=alert_type.value,
                priority=priority.value,
                message=message,
                current_value=current_value,
                threshold_value=threshold_value,
                metadata=metadata,
                status='active',
                created_at=datetime.now()
            )

            # Send notification
            await self.notification_service.send_alert(
                alert_type=alert_type.value,
                priority=priority.value,
                message=message,
                metadata={
                    'alert_id': str(alert.id),
                    'item_id': item_id,
                    'location_id': location_id,
                    **metadata or {}
                }
            )

            return alert

        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating alert: {str(e)}"
            )

    def calculate_priority(
        self,
        current_stock: float,
        threshold: float,
        lead_time: int
    ) -> AlertPriority:
        """
        Calculate alert priority based on stock level and lead time
        """
        stock_ratio = current_stock / threshold
        
        if stock_ratio <= 0:
            return AlertPriority.CRITICAL
        elif stock_ratio < 0.25:
            return AlertPriority.HIGH
        elif stock_ratio < 0.5:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW

    def calculate_expiry_priority(
        self,
        days_until_expiry: int
    ) -> AlertPriority:
        """
        Calculate priority based on days until expiry
        """
        if days_until_expiry <= 0:
            return AlertPriority.CRITICAL
        elif days_until_expiry <= 7:
            return AlertPriority.HIGH
        elif days_until_expiry <= 30:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW

    def calculate_overstock_priority(
        self,
        excess_percentage: float
    ) -> AlertPriority:
        """
        Calculate priority based on overstock percentage
        """
        if excess_percentage >= 100:
            return AlertPriority.HIGH
        elif excess_percentage >= 50:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW
