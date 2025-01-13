from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
from fastapi import HTTPException, WebSocket
from geopy.distance import geodesic
from app.core.config import Settings
from app.core.logging import logger
from app.models.tracking import (
    LocationUpdate,
    Geofence,
    VehicleTelemetry,
    DriverStatus,
    TrackingSession,
    OfflineData
)

class TrackingService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tracking_interval = settings.tracking.update_interval
        self.geofence_buffer = settings.tracking.geofence_buffer
        self.active_sessions = {}  # WebSocket connections by device_id
        self.offline_queue = asyncio.Queue()  # Queue for offline data sync

    async def start_tracking_session(
        self,
        device_id: str,
        driver_id: str,
        vehicle_id: str
    ) -> TrackingSession:
        """
        Start a new tracking session
        """
        try:
            # Create new tracking session
            session = await TrackingSession.create(
                device_id=device_id,
                driver_id=driver_id,
                vehicle_id=vehicle_id,
                status='active',
                start_time=datetime.now(),
                created_at=datetime.now()
            )

            # Initialize tracking metrics
            await self.initialize_tracking_metrics(session)

            return session

        except Exception as e:
            logger.error(f"Error starting tracking session: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error starting tracking session: {str(e)}"
            )

    async def handle_location_update(
        self,
        device_id: str,
        location_data: Dict
    ) -> LocationUpdate:
        """
        Process real-time location updates
        """
        try:
            # Validate location data
            self.validate_location_data(location_data)

            # Create location update record
            location_update = await LocationUpdate.create(
                device_id=device_id,
                latitude=location_data['latitude'],
                longitude=location_data['longitude'],
                accuracy=location_data.get('accuracy'),
                speed=location_data.get('speed'),
                bearing=location_data.get('bearing'),
                altitude=location_data.get('altitude'),
                timestamp=datetime.now(),
                created_at=datetime.now()
            )

            # Check geofences
            await self.check_geofence_triggers(device_id, location_update)

            # Update ETA calculations
            await self.update_eta(device_id, location_update)

            # Broadcast location update to subscribers
            await self.broadcast_location_update(device_id, location_update)

            return location_update

        except Exception as e:
            logger.error(f"Error handling location update: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error handling location update: {str(e)}"
            )

    async def handle_telemetry_data(
        self,
        device_id: str,
        telemetry_data: Dict
    ) -> VehicleTelemetry:
        """
        Process vehicle telemetry data
        """
        try:
            # Create telemetry record
            telemetry = await VehicleTelemetry.create(
                device_id=device_id,
                fuel_level=telemetry_data.get('fuel_level'),
                battery_level=telemetry_data.get('battery_level'),
                engine_temp=telemetry_data.get('engine_temp'),
                tire_pressure=telemetry_data.get('tire_pressure'),
                odometer=telemetry_data.get('odometer'),
                engine_status=telemetry_data.get('engine_status'),
                timestamp=datetime.now(),
                created_at=datetime.now()
            )

            # Check for alerts
            await self.check_telemetry_alerts(device_id, telemetry)

            return telemetry

        except Exception as e:
            logger.error(f"Error handling telemetry data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error handling telemetry data: {str(e)}"
            )

    async def update_driver_status(
        self,
        driver_id: str,
        status_data: Dict
    ) -> DriverStatus:
        """
        Update driver status and monitoring
        """
        try:
            # Create status update record
            status = await DriverStatus.create(
                driver_id=driver_id,
                status=status_data['status'],
                location=status_data.get('location'),
                activity=status_data.get('activity'),
                timestamp=datetime.now(),
                created_at=datetime.now()
            )

            # Check driver hours and breaks
            await self.check_driver_compliance(driver_id, status)

            return status

        except Exception as e:
            logger.error(f"Error updating driver status: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error updating driver status: {str(e)}"
            )

    async def manage_geofence(
        self,
        action: str,
        geofence_data: Dict
    ) -> Geofence:
        """
        Create or update geofence
        """
        try:
            if action == 'create':
                geofence = await Geofence.create(
                    name=geofence_data['name'],
                    type=geofence_data['type'],
                    coordinates=geofence_data['coordinates'],
                    radius=geofence_data.get('radius'),
                    triggers=geofence_data.get('triggers', []),
                    created_at=datetime.now()
                )
            else:
                geofence = await Geofence.get(id=geofence_data['id'])
                await geofence.update_from_dict(geofence_data)
                await geofence.save()

            return geofence

        except Exception as e:
            logger.error(f"Error managing geofence: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error managing geofence: {str(e)}"
            )

    async def sync_offline_data(
        self,
        device_id: str,
        offline_data: List[Dict]
    ) -> List[Dict]:
        """
        Synchronize offline tracking data
        """
        try:
            processed_records = []
            for record in offline_data:
                # Create offline data record
                offline_record = await OfflineData.create(
                    device_id=device_id,
                    data_type=record['type'],
                    data=record['data'],
                    timestamp=record['timestamp'],
                    created_at=datetime.now()
                )

                # Process based on data type
                if record['type'] == 'location':
                    await self.handle_location_update(device_id, record['data'])
                elif record['type'] == 'telemetry':
                    await self.handle_telemetry_data(device_id, record['data'])
                elif record['type'] == 'status':
                    await self.update_driver_status(record['data']['driver_id'], record['data'])

                processed_records.append({
                    'id': str(offline_record.id),
                    'status': 'processed'
                })

            return processed_records

        except Exception as e:
            logger.error(f"Error syncing offline data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error syncing offline data: {str(e)}"
            )

    async def get_location_history(
        self,
        device_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[LocationUpdate]:
        """
        Retrieve location history for playback
        """
        try:
            return await LocationUpdate.filter(
                device_id=device_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            ).order_by('timestamp')

        except Exception as e:
            logger.error(f"Error retrieving location history: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving location history: {str(e)}"
            )

    async def calculate_eta(
        self,
        device_id: str,
        destination: Dict
    ) -> Dict:
        """
        Calculate ETA based on current location and conditions
        """
        try:
            # Get current location
            current_location = await self.get_current_location(device_id)

            # Get route and traffic data
            route_data = await self.get_route_data(
                current_location,
                destination
            )

            # Calculate ETA
            eta = datetime.now() + timedelta(
                seconds=route_data['duration']
            )

            return {
                'eta': eta,
                'distance_remaining': route_data['distance'],
                'duration_remaining': route_data['duration']
            }

        except Exception as e:
            logger.error(f"Error calculating ETA: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating ETA: {str(e)}"
            )

    async def handle_websocket_connection(
        self,
        websocket: WebSocket,
        device_id: str
    ):
        """
        Handle WebSocket connection for real-time tracking
        """
        try:
            await websocket.accept()
            self.active_sessions[device_id] = websocket

            try:
                while True:
                    data = await websocket.receive_json()
                    
                    # Process received data based on type
                    if data['type'] == 'location':
                        await self.handle_location_update(device_id, data['data'])
                    elif data['type'] == 'telemetry':
                        await self.handle_telemetry_data(device_id, data['data'])
                    elif data['type'] == 'status':
                        await self.update_driver_status(data['data']['driver_id'], data['data'])

            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                raise

            finally:
                await self.cleanup_websocket_connection(device_id)

        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {str(e)}")
            raise

    def validate_location_data(self, location_data: Dict):
        """
        Validate location update data
        """
        required_fields = ['latitude', 'longitude']
        for field in required_fields:
            if field not in location_data:
                raise ValueError(f"Missing required field: {field}")

        if not (-90 <= location_data['latitude'] <= 90):
            raise ValueError("Invalid latitude value")
        if not (-180 <= location_data['longitude'] <= 180):
            raise ValueError("Invalid longitude value")

    async def check_geofence_triggers(
        self,
        device_id: str,
        location: LocationUpdate
    ):
        """
        Check for geofence triggers
        """
        geofences = await Geofence.all()
        
        for geofence in geofences:
            # Calculate distance to geofence
            distance = self.calculate_distance_to_geofence(
                location,
                geofence
            )

            # Check if device is within geofence
            if distance <= geofence.radius + self.geofence_buffer:
                await self.handle_geofence_trigger(
                    device_id,
                    geofence,
                    'enter' if distance <= geofence.radius else 'approach'
                )

    def calculate_distance_to_geofence(
        self,
        location: LocationUpdate,
        geofence: Geofence
    ) -> float:
        """
        Calculate distance between location and geofence center
        """
        return geodesic(
            (location.latitude, location.longitude),
            (geofence.coordinates['latitude'], geofence.coordinates['longitude'])
        ).meters

    async def broadcast_location_update(
        self,
        device_id: str,
        location: LocationUpdate
    ):
        """
        Broadcast location update to subscribers
        """
        if device_id in self.active_sessions:
            websocket = self.active_sessions[device_id]
            try:
                await websocket.send_json({
                    'type': 'location_update',
                    'data': {
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'timestamp': location.timestamp.isoformat(),
                        'speed': location.speed,
                        'bearing': location.bearing
                    }
                })
            except Exception as e:
                logger.error(f"Error broadcasting location update: {str(e)}")
                await self.cleanup_websocket_connection(device_id)

    async def cleanup_websocket_connection(self, device_id: str):
        """
        Clean up WebSocket connection
        """
        if device_id in self.active_sessions:
            websocket = self.active_sessions[device_id]
            try:
                await websocket.close()
            except Exception:
                pass
            finally:
                del self.active_sessions[device_id]
