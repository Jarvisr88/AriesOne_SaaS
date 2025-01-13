from typing import List
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from fastapi import HTTPException

from app.core.logging import logger

class TimeSeriesAnalyzer:
    def __init__(self):
        self.seasonal_periods = {
            'daily': 7,      # Weekly seasonality
            'weekly': 52,    # Yearly seasonality
            'monthly': 12    # Yearly seasonality
        }

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add time series features to the dataframe
        """
        try:
            # Ensure date column is datetime
            df['date'] = pd.to_datetime(df['date'])

            # Add basic time features
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['day'] = df['date'].dt.day
            df['day_of_week'] = df['date'].dt.dayofweek
            df['quarter'] = df['date'].dt.quarter
            df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6]).astype(int)
            df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
            df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
            df['is_quarter_start'] = df['date'].dt.is_quarter_start.astype(int)
            df['is_quarter_end'] = df['date'].dt.is_quarter_end.astype(int)
            df['is_year_start'] = df['date'].dt.is_year_start.astype(int)
            df['is_year_end'] = df['date'].dt.is_year_end.astype(int)

            # Add cyclical features
            df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
            df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
            df['day_sin'] = np.sin(2 * np.pi * df['day']/31)
            df['day_cos'] = np.cos(2 * np.pi * df['day']/31)
            df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week']/7)
            df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week']/7)

            if 'quantity' in df.columns:
                # Add lagged features
                for lag in [1, 7, 14, 30]:
                    df[f'lag_{lag}'] = df['quantity'].shift(lag)

                # Add rolling statistics
                for window in [7, 14, 30]:
                    df[f'rolling_mean_{window}'] = df['quantity'].rolling(window=window).mean()
                    df[f'rolling_std_{window}'] = df['quantity'].rolling(window=window).std()
                    df[f'rolling_min_{window}'] = df['quantity'].rolling(window=window).min()
                    df[f'rolling_max_{window}'] = df['quantity'].rolling(window=window).max()

                # Add expanding statistics
                df['expanding_mean'] = df['quantity'].expanding().mean()
                df['expanding_std'] = df['quantity'].expanding().std()

                # Add seasonal decomposition
                try:
                    decomposition = seasonal_decompose(
                        df['quantity'],
                        period=self.seasonal_periods['daily'],
                        extrapolate_trend='freq'
                    )
                    df['seasonal'] = decomposition.seasonal
                    df['trend'] = decomposition.trend
                    df['residual'] = decomposition.resid
                except Exception as e:
                    logger.warning(f"Could not perform seasonal decomposition: {str(e)}")

            # Fill NaN values
            df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)

            return df

        except Exception as e:
            logger.error(f"Error adding time series features: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error adding time series features: {str(e)}"
            )

    def detect_seasonality(
        self,
        data: List[float],
        freq: str = 'daily'
    ) -> dict:
        """
        Detect seasonality in time series data
        """
        try:
            if len(data) < 2 * self.seasonal_periods[freq]:
                return {
                    'has_seasonality': False,
                    'period': None,
                    'strength': None
                }

            # Convert to pandas series
            series = pd.Series(data)

            # Perform seasonal decomposition
            decomposition = seasonal_decompose(
                series,
                period=self.seasonal_periods[freq],
                extrapolate_trend='freq'
            )

            # Calculate strength of seasonality
            seasonal_strength = 1 - np.var(decomposition.resid) / np.var(series - decomposition.trend)

            return {
                'has_seasonality': seasonal_strength > 0.3,
                'period': self.seasonal_periods[freq],
                'strength': float(seasonal_strength)
            }

        except Exception as e:
            logger.error(f"Error detecting seasonality: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error detecting seasonality: {str(e)}"
            )

    def analyze_trends(
        self,
        data: List[float],
        window_size: int = 30
    ) -> dict:
        """
        Analyze trends in time series data
        """
        try:
            series = pd.Series(data)
            
            # Calculate rolling statistics
            rolling_mean = series.rolling(window=window_size).mean()
            rolling_std = series.rolling(window=window_size).std()

            # Calculate trend direction and strength
            trend_direction = np.polyfit(range(len(series)), series, 1)[0]
            trend_strength = np.abs(trend_direction) / series.std()

            # Detect change points using rolling statistics
            change_points = []
            z_scores = np.abs((series - rolling_mean) / rolling_std)
            change_points = list(np.where(z_scores > 2)[0])  # Points > 2 std dev

            return {
                'trend_direction': float(trend_direction),
                'trend_strength': float(trend_strength),
                'is_trending': abs(trend_strength) > 0.1,
                'change_points': change_points,
                'volatility': float(rolling_std.mean())
            }

        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing trends: {str(e)}"
            )
