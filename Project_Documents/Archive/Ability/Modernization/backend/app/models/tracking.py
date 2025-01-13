from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class LocationUpdate(models.Model):
    id = fields.UUIDField(pk=True)
    device_id = fields.CharField(max_length=100)
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    accuracy = fields.FloatField(null=True)
    speed = fields.FloatField(null=True)
    bearing = fields.FloatField(null=True)
    altitude = fields.FloatField(null=True)
    timestamp = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "location_updates"
        indexes = (
            ("device_id", "timestamp"),
        )

class Geofence(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    type = fields.CharField(max_length=50)  # circle, polygon
    coordinates = fields.JSONField()  # center point or polygon vertices
    radius = fields.FloatField(null=True)  # for circular geofence
    triggers = fields.JSONField()  # enter, exit, approach events
    status = fields.CharField(max_length=20)  # active, inactive
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "geofences"

class VehicleTelemetry(models.Model):
    id = fields.UUIDField(pk=True)
    device_id = fields.CharField(max_length=100)
    fuel_level = fields.FloatField(null=True)
    battery_level = fields.FloatField(null=True)
    engine_temp = fields.FloatField(null=True)
    tire_pressure = fields.JSONField(null=True)  # pressure for each tire
    odometer = fields.FloatField(null=True)
    engine_status = fields.CharField(max_length=20, null=True)
    timestamp = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "vehicle_telemetry"
        indexes = (
            ("device_id", "timestamp"),
        )

class DriverStatus(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.UUIDField()
    status = fields.CharField(max_length=20)  # active, break, offline
    location = fields.JSONField(null=True)
    activity = fields.CharField(max_length=50, null=True)
    timestamp = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "driver_status"
        indexes = (
            ("driver_id", "timestamp"),
        )

class TrackingSession(models.Model):
    id = fields.UUIDField(pk=True)
    device_id = fields.CharField(max_length=100)
    driver_id = fields.UUIDField()
    vehicle_id = fields.UUIDField()
    status = fields.CharField(max_length=20)  # active, paused, ended
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField(null=True)
    total_distance = fields.FloatField(null=True)
    total_time = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tracking_sessions"

class OfflineData(models.Model):
    id = fields.UUIDField(pk=True)
    device_id = fields.CharField(max_length=100)
    data_type = fields.CharField(max_length=50)  # location, telemetry, status
    data = fields.JSONField()
    timestamp = fields.DatetimeField()
    sync_status = fields.CharField(max_length=20)  # pending, synced, failed
    created_at = fields.DatetimeField(auto_now_add=True)
    synced_at = fields.DatetimeField(null=True)

    class Meta:
        table = "offline_data"

class GeofenceEvent(models.Model):
    id = fields.UUIDField(pk=True)
    device_id = fields.CharField(max_length=100)
    geofence = fields.ForeignKeyField('models.Geofence', related_name='events')
    event_type = fields.CharField(max_length=20)  # enter, exit, approach
    location = fields.JSONField()
    timestamp = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "geofence_events"

class TrackingMetrics(models.Model):
    id = fields.UUIDField(pk=True)
    session = fields.ForeignKeyField('models.TrackingSession', related_name='metrics')
    distance_traveled = fields.FloatField()
    average_speed = fields.FloatField()
    max_speed = fields.FloatField()
    idle_time = fields.FloatField()
    moving_time = fields.FloatField()
    stop_count = fields.IntField()
    fuel_consumption = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tracking_metrics"

# Pydantic models for API
class LocationUpdateCreate(BaseModel):
    device_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float]
    speed: Optional[float]
    bearing: Optional[float]
    altitude: Optional[float]

class GeofenceCreate(BaseModel):
    name: str
    type: str
    coordinates: Dict
    radius: Optional[float]
    triggers: List[str]

class VehicleTelemetryCreate(BaseModel):
    device_id: str
    fuel_level: Optional[float]
    battery_level: Optional[float]
    engine_temp: Optional[float]
    tire_pressure: Optional[Dict]
    odometer: Optional[float]
    engine_status: Optional[str]

class DriverStatusCreate(BaseModel):
    driver_id: str
    status: str
    location: Optional[Dict]
    activity: Optional[str]

class TrackingSessionCreate(BaseModel):
    device_id: str
    driver_id: str
    vehicle_id: str

class OfflineDataCreate(BaseModel):
    device_id: str
    data_type: str
    data: Dict
    timestamp: datetime
