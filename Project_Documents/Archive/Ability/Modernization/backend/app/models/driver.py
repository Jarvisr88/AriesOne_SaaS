from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class DriverStatus(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.CharField(max_length=100)
    status = fields.CharField(max_length=50)  # active, inactive, on_break
    location = fields.JSONField(null=True)  # lat, lng
    last_update = fields.DatetimeField()
    metadata = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "driver_statuses"
        indexes = (
            ("driver_id", "status"),
        )

class RouteAssignment(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.CharField(max_length=100)
    route_id = fields.CharField(max_length=100)
    waypoints = fields.JSONField()  # List of delivery points
    deliveries = fields.JSONField()  # Delivery details
    preferences = fields.JSONField(null=True)  # Route preferences
    progress = fields.FloatField(default=0.0)
    status = fields.CharField(max_length=50)  # assigned, started, completed
    start_time = fields.DatetimeField(null=True)
    end_time = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "route_assignments"
        indexes = (
            ("driver_id", "status"),
        )

class VehicleInspection(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.CharField(max_length=100)
    vehicle_id = fields.CharField(max_length=100)
    inspection_type = fields.CharField(max_length=50)  # pre_trip, post_trip
    checklist_items = fields.JSONField()  # Inspection checklist
    issues = fields.JSONField(null=True)  # Reported issues
    photos = fields.JSONField(null=True)  # Photo evidence
    location = fields.JSONField(null=True)  # Inspection location
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "vehicle_inspections"

class BreakTime(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.CharField(max_length=100)
    break_type = fields.CharField(max_length=50)  # lunch, rest
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField(null=True)
    duration = fields.IntField(null=True)  # Minutes
    location = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "break_times"
        indexes = (
            ("driver_id", "start_time"),
        )

class IssueReport(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.CharField(max_length=100)
    issue_type = fields.CharField(max_length=50)  # vehicle, delivery, other
    severity = fields.CharField(max_length=20)  # low, medium, high, critical
    description = fields.TextField()
    location = fields.JSONField(null=True)
    photos = fields.JSONField(null=True)
    delivery_id = fields.CharField(max_length=100, null=True)
    vehicle_id = fields.CharField(max_length=100, null=True)
    status = fields.CharField(
        max_length=50,
        default='new'
    )  # new, assigned, resolved
    resolution = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    resolved_at = fields.DatetimeField(null=True)

    class Meta:
        table = "issue_reports"

class OfflineData(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.CharField(max_length=100)
    sync_time = fields.DatetimeField()
    data_type = fields.CharField(max_length=50)  # cache, sync
    content = fields.JSONField()
    sync_results = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "offline_data"

# Pydantic models for API
class DriverStatusUpdate(BaseModel):
    driver_id: str
    status: str
    location: Optional[Dict[str, float]]
    metadata: Optional[Dict]

class RouteAssignmentCreate(BaseModel):
    driver_id: str
    route_id: str
    waypoints: List[Dict]
    deliveries: List[Dict]
    preferences: Optional[Dict]

class VehicleInspectionCreate(BaseModel):
    driver_id: str
    vehicle_id: str
    inspection_type: str
    checklist_items: Dict
    issues: Optional[List[Dict]]
    photos: Optional[List[str]]
    location: Optional[Dict[str, float]]

class BreakTimeCreate(BaseModel):
    driver_id: str
    break_type: str
    start_time: datetime
    location: Optional[Dict[str, float]]

class IssueReportCreate(BaseModel):
    driver_id: str
    issue_type: str
    severity: str
    description: str
    location: Optional[Dict[str, float]]
    photos: Optional[List[str]]
    delivery_id: Optional[str]
    vehicle_id: Optional[str]

class OfflineDataSync(BaseModel):
    driver_id: str
    sync_time: datetime
    data_type: str
    content: Dict

# Navigation models
class NavigationStep(BaseModel):
    instruction: str
    distance: float
    duration: float
    maneuver: str
    location: Dict[str, float]

class NavigationRoute(BaseModel):
    steps: List[NavigationStep]
    total_distance: float
    total_duration: float
    traffic_delay: Optional[float]
    alerts: Optional[List[Dict]]

# Inspection models
class InspectionItem(BaseModel):
    id: str
    name: str
    status: str
    notes: Optional[str]
    photos: Optional[List[str]]

class InspectionIssue(BaseModel):
    item_id: str
    severity: str
    description: str
    photos: Optional[List[str]]

# Break management models
class BreakSummary(BaseModel):
    total_breaks: int
    total_duration: int
    break_details: List[Dict]
    remaining_time: Optional[int]

# Vehicle models
class VehicleStatus(BaseModel):
    vehicle_id: str
    status: str
    issues: Optional[List[Dict]]
    last_inspection: Optional[Dict]
    maintenance_due: Optional[Dict]
