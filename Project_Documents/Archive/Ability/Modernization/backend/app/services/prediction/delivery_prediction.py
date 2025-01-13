from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.prediction import (
    DeliveryPrediction,
    PredictionModel,
    ModelMetrics,
    FeatureImportance
)

class DeliveryPredictionService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model_config = settings.prediction.model_config
        self.feature_columns = settings.prediction.feature_columns
        self.target_column = settings.prediction.target_column
        self.models = {}  # Cache for trained models
        self.scalers = {}  # Cache for feature scalers

    async def train_prediction_model(
        self,
        model_type: str,
        training_data: List[Dict]
    ) -> PredictionModel:
        """
        Train a new prediction model using historical data
        """
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(training_data)

            # Prepare features and target
            X = self.prepare_features(df)
            y = df[self.target_column]

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train model
            if model_type == 'random_forest':
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=None,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    random_state=42
                )
            elif model_type == 'gradient_boosting':
                model = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=3,
                    random_state=42
                )
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

            model.fit(X_train_scaled, y_train)

            # Calculate metrics
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            feature_importance = self.calculate_feature_importance(
                model,
                X.columns
            )

            # Save model and scaler
            model_id = f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.models[model_id] = model
            self.scalers[model_id] = scaler

            # Create model record
            model_record = await PredictionModel.create(
                model_id=model_id,
                model_type=model_type,
                features=list(X.columns),
                parameters=model.get_params(),
                created_at=datetime.now()
            )

            # Store metrics
            await ModelMetrics.create(
                model=model_record,
                train_score=train_score,
                test_score=test_score,
                created_at=datetime.now()
            )

            # Store feature importance
            for feature, importance in feature_importance:
                await FeatureImportance.create(
                    model=model_record,
                    feature_name=feature,
                    importance_score=importance,
                    created_at=datetime.now()
                )

            return model_record

        except Exception as e:
            logger.error(f"Error training prediction model: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error training prediction model: {str(e)}"
            )

    async def predict_delivery_time(
        self,
        delivery_data: Dict,
        model_id: Optional[str] = None
    ) -> DeliveryPrediction:
        """
        Generate delivery time prediction
        """
        try:
            # Get latest model if not specified
            if not model_id:
                model_record = await PredictionModel.filter(
                    status='active'
                ).order_by('-created_at').first()
                model_id = model_record.model_id

            # Get model and scaler
            model = self.models.get(model_id)
            scaler = self.scalers.get(model_id)
            if not model or not scaler:
                raise ValueError(f"Model {model_id} not found in cache")

            # Prepare features
            features = self.prepare_prediction_features(delivery_data)
            features_scaled = scaler.transform(features)

            # Generate prediction
            prediction = model.predict(features_scaled)[0]

            # Calculate confidence interval
            if isinstance(model, RandomForestRegressor):
                predictions = [
                    tree.predict(features_scaled)[0]
                    for tree in model.estimators_
                ]
                confidence = np.std(predictions)
            else:
                confidence = 0.1 * prediction  # Default 10% confidence interval

            # Create prediction record
            prediction_record = await DeliveryPrediction.create(
                model_id=model_id,
                input_data=delivery_data,
                predicted_time=prediction,
                confidence_interval=confidence,
                factors=self.analyze_prediction_factors(
                    model,
                    features,
                    prediction
                ),
                created_at=datetime.now()
            )

            return prediction_record

        except Exception as e:
            logger.error(f"Error generating prediction: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating prediction: {str(e)}"
            )

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for model training
        """
        # Historical delivery times
        df['avg_historical_time'] = df.groupby('route_id')['delivery_time'].transform('mean')
        df['std_historical_time'] = df.groupby('route_id')['delivery_time'].transform('std')

        # Weather impact
        df['weather_factor'] = df.apply(
            lambda x: self.calculate_weather_impact(x['weather_conditions']),
            axis=1
        )

        # Traffic patterns
        df['traffic_factor'] = df.apply(
            lambda x: self.calculate_traffic_impact(
                x['time_of_day'],
                x['day_of_week']
            ),
            axis=1
        )

        # Driver performance
        df['driver_performance'] = df.groupby('driver_id')['delivery_time'].transform('mean')
        df['driver_consistency'] = df.groupby('driver_id')['delivery_time'].transform('std')

        # Customer patterns
        df['customer_availability'] = df.apply(
            lambda x: self.calculate_customer_availability(
                x['customer_id'],
                x['time_of_day']
            ),
            axis=1
        )

        # Seasonal variations
        df['seasonal_factor'] = df.apply(
            lambda x: self.calculate_seasonal_impact(x['date']),
            axis=1
        )

        # Special events
        df['event_impact'] = df.apply(
            lambda x: self.calculate_event_impact(x['date'], x['location']),
            axis=1
        )

        return df[self.feature_columns]

    def prepare_prediction_features(self, delivery_data: Dict) -> pd.DataFrame:
        """
        Prepare features for prediction
        """
        features = {}
        
        # Add historical statistics
        features.update(
            self.get_historical_statistics(
                delivery_data['route_id'],
                delivery_data['time_of_day']
            )
        )

        # Add weather impact
        features['weather_factor'] = self.calculate_weather_impact(
            delivery_data['weather_conditions']
        )

        # Add traffic impact
        features['traffic_factor'] = self.calculate_traffic_impact(
            delivery_data['time_of_day'],
            delivery_data['day_of_week']
        )

        # Add driver performance
        driver_stats = self.get_driver_statistics(delivery_data['driver_id'])
        features.update(driver_stats)

        # Add customer patterns
        features['customer_availability'] = self.calculate_customer_availability(
            delivery_data['customer_id'],
            delivery_data['time_of_day']
        )

        # Add seasonal impact
        features['seasonal_factor'] = self.calculate_seasonal_impact(
            delivery_data['date']
        )

        # Add event impact
        features['event_impact'] = self.calculate_event_impact(
            delivery_data['date'],
            delivery_data['location']
        )

        return pd.DataFrame([features])

    def calculate_weather_impact(self, weather_conditions: Dict) -> float:
        """
        Calculate weather impact factor
        """
        impact_factors = {
            'clear': 1.0,
            'cloudy': 1.1,
            'rain': 1.3,
            'snow': 1.8,
            'storm': 2.0
        }
        return impact_factors.get(weather_conditions['condition'], 1.0)

    def calculate_traffic_impact(
        self,
        time_of_day: str,
        day_of_week: str
    ) -> float:
        """
        Calculate traffic impact factor
        """
        # Time of day factors
        time_factors = {
            'early_morning': 0.8,
            'morning_rush': 1.5,
            'midday': 1.0,
            'evening_rush': 1.6,
            'night': 0.7
        }

        # Day of week factors
        day_factors = {
            'monday': 1.1,
            'tuesday': 1.0,
            'wednesday': 1.0,
            'thursday': 1.1,
            'friday': 1.2,
            'saturday': 0.9,
            'sunday': 0.8
        }

        return time_factors.get(time_of_day, 1.0) * day_factors.get(day_of_week.lower(), 1.0)

    def calculate_customer_availability(
        self,
        customer_id: str,
        time_of_day: str
    ) -> float:
        """
        Calculate customer availability factor
        """
        # This would typically use historical delivery success rates
        # For now, using simplified time-based factors
        availability_factors = {
            'early_morning': 0.7,
            'morning': 0.9,
            'midday': 1.0,
            'afternoon': 0.9,
            'evening': 0.8,
            'night': 0.6
        }
        return availability_factors.get(time_of_day, 1.0)

    def calculate_seasonal_impact(self, date: datetime) -> float:
        """
        Calculate seasonal impact factor
        """
        month = date.month
        
        # Seasonal factors by month
        seasonal_factors = {
            12: 1.3,  # Holiday season
            1: 1.2,   # Post-holiday
            6: 1.1,   # Summer
            7: 1.1,   # Summer
            8: 1.1    # Summer
        }
        
        return seasonal_factors.get(month, 1.0)

    def calculate_event_impact(
        self,
        date: datetime,
        location: Dict
    ) -> float:
        """
        Calculate special event impact factor
        """
        # This would typically check against a database of events
        # For now, returning a default value
        return 1.0

    def calculate_feature_importance(
        self,
        model: object,
        feature_names: List[str]
    ) -> List[tuple]:
        """
        Calculate feature importance scores
        """
        importance_scores = model.feature_importances_
        feature_importance = list(zip(feature_names, importance_scores))
        return sorted(
            feature_importance,
            key=lambda x: x[1],
            reverse=True
        )

    def analyze_prediction_factors(
        self,
        model: object,
        features: pd.DataFrame,
        prediction: float
    ) -> Dict:
        """
        Analyze factors contributing to prediction
        """
        feature_importance = self.calculate_feature_importance(
            model,
            features.columns
        )
        
        return {
            'primary_factors': feature_importance[:3],
            'impact_breakdown': {
                name: float(score)
                for name, score in feature_importance
            }
        }
