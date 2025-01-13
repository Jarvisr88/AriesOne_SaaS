from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class Schedule(models.Model):
    id = fields.UUIDField(pk=True)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    region = fields.CharField(max_length=50, null=True)
    status = fields.CharField(max_length=20)  # draft, active, completed
    metrics = fields.JSONField(null=True)  # efficiency metrics
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "schedules"

class TimeSlot(models.Model):
    id = fields.UUIDField(pk=True)
    schedule = fields.ForeignKeyField('models.Schedule', related_name='time_slots')
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    driver_id = fields.UUIDField(null=True)
    order_id = fields.CharField(max_length=100, null=True)
    status = fields.CharField(max_length=20)  # available, assigned, completed
    capacity_used = fields.FloatField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "time_slots"
        indexes = (
            ("schedule_id", "start_time"),
        )

class DriverAvailability(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.UUIDField()
    date = fields.DateField()
    time_slots = fields.JSONField()  # List of available time ranges
    preferences = fields.JSONField(null=True)  # Preferred working hours, regions
    status = fields.CharField(max_length=20)  # available, unavailable, leave
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "driver_availability"
        unique_together = ("driver_id", "date")

class CustomerPreference(models.Model):
    id = fields.UUIDField(pk=True)
    customer_id = fields.CharField(max_length=100)
    preferred_days = fields.JSONField()  # List of preferred delivery days
    preferred_times = fields.JSONField()  # List of preferred time ranges
    blackout_dates = fields.JSONField(null=True)  # Dates when delivery is not possible
    special_instructions = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "customer_preferences"

class CapacityPlan(models.Model):
    id = fields.UUIDField(pk=True)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    region = fields.CharField(max_length=50, null=True)
    base_capacity = fields.JSONField()  # Capacity by time slot
    adjusted_capacity = fields.JSONField()  # Adjusted for events
    utilization = fields.JSONField(null=True)  # Actual utilization
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "capacity_plans"

class SpecialEvent(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    date = fields.DateField()
    impact = fields.CharField(max_length=20)  # high, medium, low
    affected_regions = fields.JSONField()
    capacity_adjustment = fields.FloatField()  # Multiplier for capacity
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "special_events"
        indexes = (
            ("date", "affected_regions"),
        )

class BreakSchedule(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.UUIDField()
    schedule_id = fields.UUIDField()
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    break_type = fields.CharField(max_length=20)  # lunch, rest, mandatory
    status = fields.CharField(max_length=20)  # scheduled, taken, missed
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "break_schedules"

class ScheduleConflict(models.Model):
    id = fields.UUIDField(pk=True)
    schedule_id = fields.UUIDField()
    conflict_type = fields.CharField(max_length=50)  # overlap, capacity, break
    entities = fields.JSONField()  # Affected orders, drivers, time slots
    severity = fields.CharField(max_length=20)  # high, medium, low
    resolution = fields.JSONField(null=True)  # Resolution details
    status = fields.CharField(max_length=20)  # detected, resolved, escalated
    created_at = fields.DatetimeField(auto_now_add=True)
    resolved_at = fields.DatetimeField(null=True)

    class Meta:
        table = "schedule_conflicts"

class ScheduleMetrics(models.Model):
    id = fields.UUIDField(pk=True)
    schedule_id = fields.UUIDField()
    date = fields.DateField()
    capacity_utilization = fields.FloatField()
    driver_utilization = fields.FloatField()
    on_time_rate = fields.FloatField()
    break_compliance = fields.FloatField()
    customer_satisfaction = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "schedule_metrics"

class ScheduleOptimization(models.Model):
    id = fields.UUIDField(pk=True)
    schedule_id = fields.UUIDField()
    optimization_type = fields.CharField(max_length=50)  # time_slots, capacity, breaks
    original_metrics = fields.JSONField()
    optimized_metrics = fields.JSONField()
    improvements = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "schedule_optimizations"

# Pydantic models for API
class ScheduleCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    region: Optional[str]

class TimeSlotCreate(BaseModel):
    schedule_id: str
    start_time: datetime
    end_time: datetime
    driver_id: Optional[str]
    order_id: Optional[str]

class DriverAvailabilityCreate(BaseModel):
    driver_id: str
    date: datetime
    time_slots: List[Dict]
    preferences: Optional[Dict]
    status: str

class CustomerPreferenceCreate(BaseModel):
    customer_id: str
    preferred_days: List[str]
    preferred_times: List[Dict]
    blackout_dates: Optional[List[datetime]]
    special_instructions: Optional[str]

class CapacityPlanCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    region: Optional[str]
    base_capacity: Dict

class SpecialEventCreate(BaseModel):
    name: str
    date: datetime
    impact: str
    affected_regions: List[str]
    capacity_adjustment: float
    notes: Optional[str]

class BreakScheduleCreate(BaseModel):
    driver_id: str
    schedule_id: str
    start_time: datetime
    end_time: datetime
    break_type: str
