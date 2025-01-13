from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import uuid
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from app.core.config import config_manager
from app.core.logging import logger
from app.core.monitoring import metrics
from app.models.core import (
    InventoryItem,
    Delivery,
    SyncQueue,
    DeliveryStatus
)

class InventoryMetrics:
    """Inventory management metrics"""
    def __init__(self):
        self.scan_time = metrics.histogram(
            "barcode_scan_time_seconds",
            "Barcode scanning processing time"
        )
        self.scan_success = metrics.counter(
            "barcode_scan_success_total",
            "Successful barcode scans"
        )
        self.scan_failure = metrics.counter(
            "barcode_scan_failure_total",
            "Failed barcode scans"
        )
        self.stock_level = metrics.gauge(
            "inventory_stock_level",
            "Current stock level by item",
            ["item_id", "name"]
        )

class InventoryManager:
    """Advanced inventory management service"""
    def __init__(self, db: Session):
        self.db = db
        self.metrics = InventoryMetrics()
        self._setup_service()

    def _setup_service(self):
        """Setup inventory manager"""
        self.low_stock_threshold = config_manager.get("LOW_STOCK_THRESHOLD", 10)
        self.reorder_point = config_manager.get("REORDER_POINT", 5)
        self.max_sync_retries = config_manager.get("MAX_SYNC_RETRIES", 3)

    async def scan_barcode(
        self,
        image_data: bytes,
        delivery_id: Optional[uuid.UUID] = None
    ) -> Dict:
        """Scan barcode from image"""
        try:
            start_time = datetime.utcnow()
            
            # Convert image data to OpenCV format
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            
            # Enhance image for better barcode detection
            img = cv2.GaussianBlur(img, (5, 5), 0)
            img = cv2.adaptiveThreshold(
                img,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Detect barcodes
            barcodes = decode(img)
            if not barcodes:
                self.metrics.scan_failure.inc()
                raise ValueError("No barcode detected")
            
            # Process detected barcodes
            results = []
            for barcode in barcodes:
                item = await self._process_barcode(
                    barcode.data.decode(),
                    delivery_id
                )
                if item:
                    results.append(item)
            
            # Track metrics
            scan_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.scan_time.observe(scan_time)
            self.metrics.scan_success.inc()
            
            return {
                "items": results,
                "scan_time": scan_time,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Barcode scan error: {e}")
            self.metrics.scan_failure.inc()
            raise

    async def _process_barcode(
        self,
        barcode: str,
        delivery_id: Optional[uuid.UUID]
    ) -> Optional[Dict]:
        """Process scanned barcode"""
        try:
            # Find item
            item = self.db.query(InventoryItem).filter(
                InventoryItem.barcode == barcode
            ).first()
            
            if not item:
                return None
            
            # Update delivery if provided
            if delivery_id:
                delivery = self.db.query(Delivery).get(delivery_id)
                if delivery:
                    # Check if item exists in delivery
                    for delivery_item in delivery.items:
                        if delivery_item["item_id"] == str(item.id):
                            delivery_item["scanned"] = True
                            break
                    
                    self.db.commit()
            
            return {
                "item_id": str(item.id),
                "name": item.name,
                "barcode": item.barcode,
                "quantity": item.quantity
            }
            
        except Exception as e:
            logger.error(f"Barcode processing error: {e}")
            return None

    async def update_stock(
        self,
        item_id: uuid.UUID,
        quantity_change: int,
        sync: bool = True
    ) -> Dict:
        """Update item stock level"""
        try:
            item = self.db.query(InventoryItem).get(item_id)
            if not item:
                raise ValueError("Item not found")
            
            # Update quantity
            new_quantity = item.quantity + quantity_change
            if new_quantity < 0:
                raise ValueError("Insufficient stock")
            
            item.quantity = new_quantity
            item.updated_at = datetime.utcnow()
            
            # Add to sync queue if offline
            if not sync:
                await self._queue_sync_operation(
                    "stock_update",
                    {
                        "item_id": str(item_id),
                        "quantity_change": quantity_change
                    }
                )
            
            self.db.commit()
            
            # Update metrics
            self.metrics.stock_level.labels(
                item_id=str(item.id),
                name=item.name
            ).set(new_quantity)
            
            # Check stock level
            if new_quantity <= self.reorder_point:
                await self._trigger_reorder(item)
            
            return {
                "item_id": str(item.id),
                "name": item.name,
                "new_quantity": new_quantity,
                "low_stock": new_quantity <= self.low_stock_threshold
            }
            
        except Exception as e:
            logger.error(f"Stock update error: {e}")
            raise

    async def _trigger_reorder(
        self,
        item: InventoryItem
    ) -> None:
        """Trigger item reorder"""
        try:
            # Calculate reorder quantity
            usage_rate = await self._calculate_usage_rate(item)
            reorder_quantity = max(
                int(usage_rate * 7),  # 1 week supply
                self.low_stock_threshold - item.quantity
            )
            
            # Create reorder event
            await self._queue_sync_operation(
                "reorder",
                {
                    "item_id": str(item.id),
                    "quantity": reorder_quantity,
                    "priority": "HIGH" if item.quantity <= self.reorder_point else "NORMAL"
                }
            )
            
        except Exception as e:
            logger.error(f"Reorder trigger error: {e}")

    async def _calculate_usage_rate(
        self,
        item: InventoryItem
    ) -> float:
        """Calculate item usage rate"""
        try:
            # Get usage history
            start_date = datetime.utcnow() - timedelta(days=30)
            deliveries = self.db.query(Delivery).filter(
                and_(
                    Delivery.created_at >= start_date,
                    Delivery.status == DeliveryStatus.DELIVERED
                )
            ).all()
            
            # Calculate total usage
            total_usage = 0
            for delivery in deliveries:
                for delivery_item in delivery.items:
                    if delivery_item["item_id"] == str(item.id):
                        total_usage += delivery_item["quantity"]
            
            # Calculate daily rate
            return total_usage / 30
            
        except Exception as e:
            logger.error(f"Usage rate calculation error: {e}")
            return 0

    async def process_sync_queue(self) -> Dict:
        """Process offline sync queue"""
        try:
            # Get unprocessed items
            queue_items = self.db.query(SyncQueue).filter(
                SyncQueue.processed == False
            ).all()
            
            results = {
                "processed": 0,
                "failed": 0,
                "retried": 0
            }
            
            for item in queue_items:
                try:
                    # Process based on type
                    if item.type == "stock_update":
                        await self.update_stock(
                            uuid.UUID(item.data["item_id"]),
                            item.data["quantity_change"],
                            sync=True
                        )
                    elif item.type == "reorder":
                        # Process reorder
                        pass
                    
                    item.processed = True
                    item.processed_at = datetime.utcnow()
                    results["processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Sync processing error: {e}")
                    results["failed"] += 1
            
            self.db.commit()
            return results
            
        except Exception as e:
            logger.error(f"Sync queue processing error: {e}")
            raise

    async def _queue_sync_operation(
        self,
        type: str,
        data: Dict
    ) -> None:
        """Add operation to sync queue"""
        try:
            queue_item = SyncQueue(
                type=type,
                data=data
            )
            self.db.add(queue_item)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Sync queue error: {e}")
            raise

    async def get_inventory_status(
        self,
        category: Optional[str] = None
    ) -> Dict:
        """Get inventory status"""
        try:
            # Build query
            query = self.db.query(InventoryItem)
            if category:
                query = query.filter(InventoryItem.category == category)
            
            items = query.all()
            
            # Calculate statistics
            total_items = len(items)
            low_stock = sum(1 for item in items if item.quantity <= self.low_stock_threshold)
            zero_stock = sum(1 for item in items if item.quantity == 0)
            
            return {
                "total_items": total_items,
                "low_stock_items": low_stock,
                "zero_stock_items": zero_stock,
                "items": [
                    {
                        "item_id": str(item.id),
                        "name": item.name,
                        "quantity": item.quantity,
                        "category": item.category,
                        "low_stock": item.quantity <= self.low_stock_threshold,
                        "last_updated": item.updated_at.isoformat()
                    }
                    for item in items
                ]
            }
            
        except Exception as e:
            logger.error(f"Inventory status error: {e}")
            raise

# Create inventory manager factory
def get_inventory_manager(db: Session) -> InventoryManager:
    return InventoryManager(db)
