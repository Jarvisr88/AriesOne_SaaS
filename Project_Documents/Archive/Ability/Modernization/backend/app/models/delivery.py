from datetime import datetime, timedelta
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class Vehicle(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    type = fields.CharField(max_length=50)  # van, truck, etc.
    license_plate = fields.CharField(max_length=20)
    capacity = fields.FloatField()  # volume capacity
    weight_capacity = fields.FloatField()
    fuel_type = fields.CharField(max_length=20)  # gas, diesel, electric
    fuel_efficiency = fields.FloatField()  # miles per gallon or kWh
    maintenance_status = fields.CharField(max_length=20)  # active, maintenance, inactive
    last_maintenance = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "vehicles"

class Driver(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    license_number = fields.CharField(max_length=50)
    license_type = fields.CharField(max_length=20)
    license_expiry = fields.DateField()
    phone = fields.CharField(max_length=20)
    email = fields.CharField(max_length=100)
    status = fields.CharField(max_length=20)  # active, break, off-duty
    current_location = fields.JSONField(null=True)  # lat, lng
    total_hours = fields.FloatField(default=0)  # hours worked today
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "drivers"

class DeliveryStop(models.Model):
    id = fields.UUIDField(pk=True)
    order = fields.ForeignKeyField('models.Order', related_name='delivery_stops')
    sequence = fields.IntField()  # position in route
    location = fields.JSONField()  # address and coordinates
    time_window = fields.JSONField()  # delivery time window
    service_time = fields.IntField()  # minutes needed at stop
    volume = fields.FloatField()  # total volume of items
    weight = fields.FloatField()  # total weight of items
    status = fields.CharField(max_length=20)  # pending, completed, failed
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "delivery_stops"

class Route(models.Model):
    id = fields.UUIDField(pk=True)
    vehicle = fields.ForeignKeyField('models.Vehicle', related_name='routes')
    driver = fields.ForeignKeyField('models.Driver', related_name='routes')
    date = fields.DateField()
    stops = fields.JSONField()  # ordered list of stops with timing
    status = fields.CharField(max_length=20)  # scheduled, in_progress, completed
    start_time = fields.DatetimeField(null=True)
    end_time = fields.DatetimeField(null=True)
    total_distance = fields.FloatField(null=True)
    total_time = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "routes"

class TrafficData(models.Model):
    id = fields.UUIDField(pk=True)
    timestamp = fields.DatetimeField()
    region = fields.CharField(max_length=50)
    data = fields.JSONField()  # traffic conditions by segment
    source = fields.CharField(max_length=50)  # traffic data provider
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "traffic_data"

class RouteMetrics(models.Model):
    id = fields.UUIDField(pk=True)
    route = fields.ForeignKeyField('models.Route', related_name='metrics')
    total_distance = fields.FloatField()
    total_time = fields.FloatField()
    fuel_consumption = fields.FloatField()
    efficiency_score = fields.FloatField(null=True)
    on_time_rate = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "route_metrics"

class DriverBreak(models.Model):
    id = fields.UUIDField(pk=True)
    driver = fields.ForeignKeyField('models.Driver', related_name='breaks')
    route = fields.ForeignKeyField('models.Route', related_name='breaks')
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    break_type = fields.CharField(max_length=20)  # rest, meal, mandatory
    location = fields.JSONField(null=True)  # break location
    status = fields.CharField(max_length=20)  # scheduled, in_progress, completed
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "driver_breaks"

# Pydantic models for API
class VehicleCreate(BaseModel):
    name: str
    type: str
    license_plate: str
    capacity: float
    weight_capacity: float
    fuel_type: str
    fuel_efficiency: float

class DriverCreate(BaseModel):
    name: str
    license_number: str
    license_type: str
    license_expiry: datetime
    phone: str
    email: str

class DeliveryStopCreate(BaseModel):
    order_id: str
    sequence: int
    location: Dict
    time_window: Dict
    service_time: int
    volume: float
    weight: float
    notes: Optional[str]

class RouteCreate(BaseModel):
    vehicle_id: str
    driver_id: str
    date: datetime
    stops: List[Dict]

class RouteMetricsCreate(BaseModel):
    route_id: str
    total_distance: float
    total_time: float
    fuel_consumption: float
    efficiency_score: Optional[float]
    on_time_rate: Optional[float]

class DriverBreakCreate(BaseModel):
    driver_id: str
    route_id: str
    start_time: datetime
    end_time: datetime
    break_type: str
    location: Optional[Dict]
