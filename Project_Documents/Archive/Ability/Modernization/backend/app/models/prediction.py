from datetime import datetime
from typing import Optional, Dict, List
from tortoise import fields, models
from pydantic import BaseModel

class PredictionModel(models.Model):
    id = fields.UUIDField(pk=True)
    model_id = fields.CharField(max_length=100, unique=True)
    model_type = fields.CharField(max_length=50)  # random_forest, gradient_boosting
    features = fields.JSONField()  # List of feature names
    parameters = fields.JSONField()  # Model hyperparameters
    status = fields.CharField(max_length=20, default='active')  # active, archived
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "prediction_models"

class ModelMetrics(models.Model):
    id = fields.UUIDField(pk=True)
    model = fields.ForeignKeyField('models.PredictionModel', related_name='metrics')
    train_score = fields.FloatField()
    test_score = fields.FloatField()
    mae = fields.FloatField(null=True)  # Mean Absolute Error
    mse = fields.FloatField(null=True)  # Mean Squared Error
    rmse = fields.FloatField(null=True)  # Root Mean Squared Error
    r2_score = fields.FloatField(null=True)  # R-squared Score
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "model_metrics"

class FeatureImportance(models.Model):
    id = fields.UUIDField(pk=True)
    model = fields.ForeignKeyField('models.PredictionModel', related_name='feature_importance')
    feature_name = fields.CharField(max_length=100)
    importance_score = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "feature_importance"
        unique_together = ("model", "feature_name")

class DeliveryPrediction(models.Model):
    id = fields.UUIDField(pk=True)
    model_id = fields.CharField(max_length=100)
    input_data = fields.JSONField()  # Input features
    predicted_time = fields.FloatField()  # Predicted delivery time
    confidence_interval = fields.FloatField()  # Prediction confidence
    actual_time = fields.FloatField(null=True)  # Actual delivery time when available
    error = fields.FloatField(null=True)  # Prediction error
    factors = fields.JSONField()  # Contributing factors
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "delivery_predictions"

class WeatherData(models.Model):
    id = fields.UUIDField(pk=True)
    location = fields.JSONField()  # lat, lng
    timestamp = fields.DatetimeField()
    conditions = fields.JSONField()  # temperature, precipitation, wind, etc.
    source = fields.CharField(max_length=50)  # weather data provider
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "weather_data"
        indexes = (
            ("location", "timestamp"),
        )

class TrafficPattern(models.Model):
    id = fields.UUIDField(pk=True)
    route_id = fields.CharField(max_length=100)
    day_of_week = fields.CharField(max_length=10)
    time_of_day = fields.CharField(max_length=20)
    average_speed = fields.FloatField()
    congestion_level = fields.FloatField()
    sample_size = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "traffic_patterns"
        unique_together = ("route_id", "day_of_week", "time_of_day")

class DriverPerformance(models.Model):
    id = fields.UUIDField(pk=True)
    driver_id = fields.UUIDField()
    route_type = fields.CharField(max_length=50)
    average_speed = fields.FloatField()
    delivery_accuracy = fields.FloatField()  # percentage of on-time deliveries
    efficiency_score = fields.FloatField()
    sample_size = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "driver_performance"
        unique_together = ("driver_id", "route_type")

class CustomerPattern(models.Model):
    id = fields.UUIDField(pk=True)
    customer_id = fields.CharField(max_length=100)
    preferred_time = fields.JSONField()  # time windows with success rates
    success_rate = fields.FloatField()  # overall delivery success rate
    average_wait_time = fields.FloatField()
    sample_size = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "customer_patterns"

class SeasonalPattern(models.Model):
    id = fields.UUIDField(pk=True)
    month = fields.IntField()
    region = fields.CharField(max_length=50)
    delivery_factor = fields.FloatField()  # multiplier for delivery times
    volume_factor = fields.FloatField()  # multiplier for delivery volume
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "seasonal_patterns"
        unique_together = ("month", "region")

class SpecialEvent(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    location = fields.JSONField()  # affected area
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    impact_level = fields.FloatField()  # multiplier for delivery times
    affected_routes = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "special_events"

# Pydantic models for API
class PredictionModelCreate(BaseModel):
    model_type: str
    features: List[str]
    parameters: Dict

class DeliveryPredictionCreate(BaseModel):
    route_id: str
    driver_id: str
    customer_id: str
    time_of_day: str
    day_of_week: str
    weather_conditions: Dict
    location: Dict
    date: datetime

class WeatherDataCreate(BaseModel):
    location: Dict
    conditions: Dict
    source: str

class TrafficPatternCreate(BaseModel):
    route_id: str
    day_of_week: str
    time_of_day: str
    average_speed: float
    congestion_level: float
    sample_size: int

class DriverPerformanceCreate(BaseModel):
    driver_id: str
    route_type: str
    average_speed: float
    delivery_accuracy: float
    efficiency_score: float
    sample_size: int

class CustomerPatternCreate(BaseModel):
    customer_id: str
    preferred_time: Dict
    success_rate: float
    average_wait_time: float
    sample_size: int

class SpecialEventCreate(BaseModel):
    name: str
    location: Dict
    start_time: datetime
    end_time: datetime
    impact_level: float
    affected_routes: List[str]
