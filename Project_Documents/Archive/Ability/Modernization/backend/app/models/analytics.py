from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class PerformanceMetric(models.Model):
    id = fields.UUIDField(pk=True)
    metric_type = fields.CharField(max_length=50)
    value = fields.FloatField()
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    metadata = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "performance_metrics"
        indexes = (
            ("metric_type", "start_date", "end_date"),
        )

class RouteAnalysis(models.Model):
    id = fields.UUIDField(pk=True)
    route_id = fields.CharField(max_length=100)
    metrics = fields.JSONField()  # Efficiency metrics
    opportunities = fields.JSONField()  # Optimization opportunities
    recommendations = fields.JSONField()  # Improvement recommendations
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "route_analyses"

class DriverPerformance(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.CharField(max_length=100)
    metrics = fields.JSONField()  # Performance metrics
    trends = fields.JSONField()  # Performance trends
    insights = fields.JSONField()  # Performance insights
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "driver_performances"
        indexes = (
            ("driver_id", "start_date", "end_date"),
        )

class CustomerMetric(models.Model):
    id = fields.UUIDField(pk=True)
    metrics = fields.JSONField()  # Satisfaction metrics
    patterns = fields.JSONField()  # Feedback patterns
    improvements = fields.JSONField()  # Areas for improvement
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "customer_metrics"

class AnalyticsReport(models.Model):
    id = fields.UUIDField(pk=True)
    report_type = fields.CharField(max_length=50)
    parameters = fields.JSONField()  # Report parameters
    metrics = fields.JSONField()  # Calculated metrics
    visualizations = fields.JSONField()  # Generated visualizations
    insights = fields.JSONField()  # Key insights
    recommendations = fields.JSONField()  # Action recommendations
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "analytics_reports"

class MetricThreshold(models.Model):
    id = fields.UUIDField(pk=True)
    metric_type = fields.CharField(max_length=50)
    warning_threshold = fields.FloatField()
    critical_threshold = fields.FloatField()
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "metric_thresholds"

class AnalyticsAlert(models.Model):
    id = fields.UUIDField(pk=True)
    metric_type = fields.CharField(max_length=50)
    threshold_id = fields.CharField(max_length=100)
    current_value = fields.FloatField()
    severity = fields.CharField(max_length=20)
    status = fields.CharField(max_length=20)  # new, acknowledged, resolved
    created_at = fields.DatetimeField(auto_now_add=True)
    resolved_at = fields.DatetimeField(null=True)

    class Meta:
        table = "analytics_alerts"

# Pydantic models for API
class PerformanceMetricCreate(BaseModel):
    metric_type: str
    value: float
    start_date: datetime
    end_date: datetime
    metadata: Optional[Dict]

class RouteAnalysisCreate(BaseModel):
    route_id: str
    metrics: Dict
    opportunities: List[Dict]
    recommendations: List[str]

class DriverPerformanceCreate(BaseModel):
    driver_id: str
    metrics: Dict
    trends: Dict
    insights: List[str]
    start_date: datetime
    end_date: datetime

class CustomerMetricCreate(BaseModel):
    metrics: Dict
    patterns: Dict
    improvements: List[Dict]
    start_date: datetime
    end_date: datetime

class AnalyticsReportCreate(BaseModel):
    report_type: str
    parameters: Dict
    metrics: Dict
    visualizations: Dict
    insights: List[str]
    recommendations: List[str]

class MetricThresholdCreate(BaseModel):
    metric_type: str
    warning_threshold: float
    critical_threshold: float
    is_active: Optional[bool] = True

class AnalyticsAlertCreate(BaseModel):
    metric_type: str
    threshold_id: str
    current_value: float
    severity: str
    status: str = 'new'
