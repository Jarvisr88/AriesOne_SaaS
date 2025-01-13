from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid
import asyncio
from sqlalchemy.orm import Session
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import osmnx as ox
import networkx as nx
from app.core.config import config_manager
from app.core.logging import logger
from app.core.monitoring import metrics
from app.core.events import event_bus
from app.models.core import (
    Delivery,
    DeliveryStatus,
    Location,
    Route,
    Vehicle,
    InventoryItem,
    SyncQueue
)

class DeliveryMetrics:
    """Delivery metrics tracking"""
    def __init__(self):
        self.active_deliveries = metrics.gauge(
            "delivery_active_total",
            "Total active deliveries"
        )
        self.completed_deliveries = metrics.counter(
            "delivery_completed_total",
            "Total completed deliveries"
        )
        self.delivery_time = metrics.histogram(
            "delivery_time_seconds",
            "Delivery completion time"
        )
        self.route_distance = metrics.histogram(
            "route_distance_meters",
            "Route distance in meters"
        )
        self.offline_syncs = metrics.counter(
            "offline_syncs_total",
            "Total offline synchronizations"
        )

class DeliveryService:
    """Delivery and tracking service"""
    def __init__(self, db: Session):
        self.db = db
        self.metrics = DeliveryMetrics()
        self.geolocator = Nominatim(user_agent="ariesone")
        self.graph = None
        self._setup_service()

    def _setup_service(self):
        """Setup delivery service"""
        self.update_interval = config_manager.get("GPS_UPDATE_INTERVAL", 30)
        self.offline_sync_interval = config_manager.get("OFFLINE_SYNC_INTERVAL", 300)
        self.max_route_distance = config_manager.get("MAX_ROUTE_DISTANCE", 100000)
        self.min_accuracy = config_manager.get("MIN_GPS_ACCURACY", 10)
        self._setup_background_tasks()

    def _setup_background_tasks(self):
        """Setup background processing tasks"""
        asyncio.create_task(self._process_offline_syncs())
        asyncio.create_task(self._update_active_deliveries())

    async def create_delivery(
        self,
        items: List[Dict],
        destination: Dict,
        vehicle_id: uuid.UUID,
        priority: str = "NORMAL"
    ) -> Delivery:
        """Create new delivery"""
        try:
            # Validate items
            inventory_items = []
            for item in items:
                inv_item = self.db.query(InventoryItem).get(item["id"])
                if not inv_item or inv_item.quantity < item["quantity"]:
                    raise ValueError(f"Insufficient stock for item {item['id']}")
                inventory_items.append((inv_item, item["quantity"]))

            # Geocode destination
            location = await self._geocode_address(destination)
            
            # Create delivery
            delivery = Delivery(
                status=DeliveryStatus.PENDING,
                priority=priority,
                destination=location,
                vehicle_id=vehicle_id
            )
            
            # Allocate inventory
            for inv_item, quantity in inventory_items:
                inv_item.quantity -= quantity
                delivery.items.append({
                    "item_id": str(inv_item.id),
                    "quantity": quantity
                })
            
            self.db.add(delivery)
            self.db.commit()
            
            # Update metrics
            self.metrics.active_deliveries.inc()
            
            # Emit event
            await event_bus.emit({
                "type": "delivery_created",
                "data": {
                    "delivery_id": str(delivery.id),
                    "destination": destination,
                    "items": delivery.items
                }
            })
            
            return delivery
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Delivery creation error: {e}")
            raise

    async def update_location(
        self,
        delivery_id: uuid.UUID,
        latitude: float,
        longitude: float,
        accuracy: float,
        timestamp: datetime,
        offline: bool = False
    ) -> Location:
        """Update delivery location"""
        try:
            if offline:
                # Queue update for sync
                return await self._queue_location_update(
                    delivery_id,
                    latitude,
                    longitude,
                    accuracy,
                    timestamp
                )
            
            if accuracy > self.min_accuracy:
                logger.warning(f"Low GPS accuracy: {accuracy}")
            
            # Create location
            location = Location(
                delivery_id=delivery_id,
                latitude=latitude,
                longitude=longitude,
                accuracy=accuracy,
                timestamp=timestamp
            )
            
            # Update delivery route
            delivery = self.db.query(Delivery).get(delivery_id)
            if delivery:
                await self._update_route(delivery, location)
            
            self.db.add(location)
            self.db.commit()
            
            # Emit event
            await event_bus.emit({
                "type": "location_updated",
                "data": {
                    "delivery_id": str(delivery_id),
                    "latitude": latitude,
                    "longitude": longitude,
                    "timestamp": timestamp.isoformat()
                }
            })
            
            return location
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Location update error: {e}")
            raise

    async def _queue_location_update(
        self,
        delivery_id: uuid.UUID,
        latitude: float,
        longitude: float,
        accuracy: float,
        timestamp: datetime
    ) -> None:
        """Queue location update for offline sync"""
        try:
            sync_item = SyncQueue(
                type="LOCATION",
                data={
                    "delivery_id": str(delivery_id),
                    "latitude": latitude,
                    "longitude": longitude,
                    "accuracy": accuracy,
                    "timestamp": timestamp.isoformat()
                }
            )
            self.db.add(sync_item)
            self.db.commit()
            
            # Update metrics
            self.metrics.offline_syncs.inc()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Sync queue error: {e}")
            raise

    async def _process_offline_syncs(self):
        """Process offline sync queue"""
        while True:
            try:
                # Get queued items
                items = self.db.query(SyncQueue).filter(
                    SyncQueue.processed == False
                ).all()
                
                for item in items:
                    if item.type == "LOCATION":
                        # Process location update
                        await self.update_location(
                            uuid.UUID(item.data["delivery_id"]),
                            item.data["latitude"],
                            item.data["longitude"],
                            item.data["accuracy"],
                            datetime.fromisoformat(item.data["timestamp"])
                        )
                        
                    item.processed = True
                    self.db.commit()
                    
            except Exception as e:
                logger.error(f"Offline sync error: {e}")
                
            await asyncio.sleep(self.offline_sync_interval)

    async def _update_active_deliveries(self):
        """Update active delivery status"""
        while True:
            try:
                # Get active deliveries
                deliveries = self.db.query(Delivery).filter(
                    Delivery.status.in_([
                        DeliveryStatus.IN_PROGRESS,
                        DeliveryStatus.PENDING
                    ])
                ).all()
                
                for delivery in deliveries:
                    # Check if arrived at destination
                    if await self._check_arrival(delivery):
                        delivery.status = DeliveryStatus.DELIVERED
                        delivery.completed_at = datetime.utcnow()
                        
                        # Update metrics
                        self.metrics.active_deliveries.dec()
                        self.metrics.completed_deliveries.inc()
                        delivery_time = (
                            delivery.completed_at - delivery.created_at
                        ).total_seconds()
                        self.metrics.delivery_time.observe(delivery_time)
                        
                        # Emit event
                        await event_bus.emit({
                            "type": "delivery_completed",
                            "data": {
                                "delivery_id": str(delivery.id),
                                "duration": delivery_time
                            }
                        })
                        
                self.db.commit()
                
            except Exception as e:
                logger.error(f"Delivery update error: {e}")
                
            await asyncio.sleep(self.update_interval)

    async def _check_arrival(self, delivery: Delivery) -> bool:
        """Check if delivery has arrived at destination"""
        if not delivery.locations:
            return False
            
        current = delivery.locations[-1]
        destination = delivery.destination
        
        distance = geodesic(
            (current.latitude, current.longitude),
            (destination.latitude, destination.longitude)
        ).meters
        
        return distance <= config_manager.get("ARRIVAL_THRESHOLD", 50)

    async def _geocode_address(self, address: Dict) -> Location:
        """Geocode address to coordinates"""
        try:
            # Format address
            address_str = ", ".join(filter(None, [
                address.get("street"),
                address.get("city"),
                address.get("state"),
                address.get("postal_code"),
                address.get("country")
            ]))
            
            # Geocode
            location = self.geolocator.geocode(address_str)
            if not location:
                raise ValueError("Unable to geocode address")
                
            return Location(
                latitude=location.latitude,
                longitude=location.longitude,
                address=address
            )
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            raise

    async def plan_route(
        self,
        delivery_id: uuid.UUID,
        optimize: bool = True
    ) -> Route:
        """Plan delivery route"""
        try:
            delivery = self.db.query(Delivery).get(delivery_id)
            if not delivery:
                raise ValueError("Delivery not found")
                
            vehicle = delivery.vehicle
            if not vehicle:
                raise ValueError("Vehicle not assigned")
                
            # Get current location
            current = vehicle.last_location
            if not current:
                raise ValueError("Vehicle location unknown")
                
            # Create route
            route = await self._calculate_route(
                (current.latitude, current.longitude),
                (delivery.destination.latitude, delivery.destination.longitude),
                optimize
            )
            
            # Save route
            route_obj = Route(
                delivery=delivery,
                path=route["path"],
                distance=route["distance"],
                duration=route["duration"]
            )
            self.db.add(route_obj)
            self.db.commit()
            
            # Update metrics
            self.metrics.route_distance.observe(route["distance"])
            
            # Emit event
            await event_bus.emit({
                "type": "route_created",
                "data": {
                    "delivery_id": str(delivery_id),
                    "distance": route["distance"],
                    "duration": route["duration"]
                }
            })
            
            return route_obj
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Route planning error: {e}")
            raise

    async def _calculate_route(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        optimize: bool
    ) -> Dict:
        """Calculate optimal route"""
        try:
            if not self.graph:
                # Download street network
                self.graph = ox.graph_from_point(
                    start,
                    dist=self.max_route_distance,
                    network_type="drive"
                )
            
            # Get nearest nodes
            start_node = ox.nearest_nodes(self.graph, start[1], start[0])
            end_node = ox.nearest_nodes(self.graph, end[1], end[0])
            
            if optimize:
                # Calculate shortest path
                path = nx.shortest_path(
                    self.graph,
                    start_node,
                    end_node,
                    weight="length"
                )
            else:
                # Calculate fastest path
                path = nx.shortest_path(
                    self.graph,
                    start_node,
                    end_node,
                    weight="travel_time"
                )
            
            # Get path coordinates
            coordinates = []
            for node in path:
                coordinates.append([
                    self.graph.nodes[node]["y"],
                    self.graph.nodes[node]["x"]
                ])
            
            # Calculate metrics
            distance = sum(
                self.graph[path[i]][path[i+1]][0]["length"]
                for i in range(len(path)-1)
            )
            duration = sum(
                self.graph[path[i]][path[i+1]][0]["travel_time"]
                for i in range(len(path)-1)
            )
            
            return {
                "path": coordinates,
                "distance": distance,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Route calculation error: {e}")
            raise

    async def scan_barcode(
        self,
        barcode: str,
        delivery_id: Optional[uuid.UUID] = None
    ) -> Dict:
        """Process barcode scan"""
        try:
            # Find item by barcode
            item = self.db.query(InventoryItem).filter(
                InventoryItem.barcode == barcode
            ).first()
            if not item:
                raise ValueError("Item not found")
                
            result = {
                "item_id": str(item.id),
                "name": item.name,
                "barcode": item.barcode,
                "quantity": item.quantity
            }
            
            if delivery_id:
                # Check if item is part of delivery
                delivery = self.db.query(Delivery).get(delivery_id)
                if delivery:
                    for delivery_item in delivery.items:
                        if delivery_item["item_id"] == str(item.id):
                            result["delivery_quantity"] = delivery_item["quantity"]
                            break
            
            # Emit event
            await event_bus.emit({
                "type": "barcode_scanned",
                "data": {
                    "barcode": barcode,
                    "item_id": str(item.id),
                    "delivery_id": str(delivery_id) if delivery_id else None
                }
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Barcode scan error: {e}")
            raise

    async def get_metrics(self) -> Dict:
        """Get delivery metrics"""
        return {
            "active_deliveries": self.metrics.active_deliveries._value.get(),
            "completed_deliveries": self.metrics.completed_deliveries._value.get(),
            "delivery_time": self.metrics.delivery_time._value.get(),
            "route_distance": self.metrics.route_distance._value.get(),
            "offline_syncs": self.metrics.offline_syncs._value.get()
        }

# Create delivery service factory
def get_delivery_service(db: Session) -> DeliveryService:
    return DeliveryService(db)
