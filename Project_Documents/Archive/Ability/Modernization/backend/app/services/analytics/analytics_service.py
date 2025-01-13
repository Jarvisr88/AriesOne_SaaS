from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.analytics import (
    PerformanceMetric,
    RouteAnalysis,
    DriverPerformance,
    CustomerMetric,
    AnalyticsReport
)

class AnalyticsService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.metrics_config = settings.analytics.metrics
        self.analysis_config = settings.analytics.analysis

    async def calculate_performance_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None
    ) -> List[PerformanceMetric]:
        """
        Calculate system-wide performance metrics
        """
        try:
            # Get raw data
            deliveries = await self._get_delivery_data(start_date, end_date)
            routes = await self._get_route_data(start_date, end_date)
            drivers = await self._get_driver_data(start_date, end_date)

            # Calculate metrics
            metrics_list = []
            for metric_type in (metrics or self.metrics_config.performance_metrics):
                value = await self._calculate_metric(
                    metric_type,
                    deliveries,
                    routes,
                    drivers
                )
                
                metrics_list.append(
                    await PerformanceMetric.create(
                        metric_type=metric_type,
                        value=value,
                        start_date=start_date,
                        end_date=end_date,
                        created_at=datetime.now()
                    )
                )

            return metrics_list

        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            raise

    async def analyze_route_efficiency(
        self,
        route_ids: Optional[List[str]] = None,
        date_range: Optional[tuple] = None
    ) -> List[RouteAnalysis]:
        """
        Analyze route efficiency metrics
        """
        try:
            # Get route data
            routes = await self._get_route_data(
                date_range[0] if date_range else None,
                date_range[1] if date_range else None,
                route_ids
            )

            analyses = []
            for route in routes:
                # Calculate efficiency metrics
                metrics = await self._calculate_route_metrics(route)

                # Identify optimization opportunities
                opportunities = self._identify_route_opportunities(
                    route,
                    metrics
                )

                # Generate recommendations
                recommendations = self._generate_route_recommendations(
                    metrics,
                    opportunities
                )

                analyses.append(
                    await RouteAnalysis.create(
                        route_id=route['id'],
                        metrics=metrics,
                        opportunities=opportunities,
                        recommendations=recommendations,
                        created_at=datetime.now()
                    )
                )

            return analyses

        except Exception as e:
            logger.error(f"Error analyzing route efficiency: {str(e)}")
            raise

    async def track_driver_performance(
        self,
        driver_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[DriverPerformance]:
        """
        Track and analyze driver performance
        """
        try:
            # Get driver data
            drivers = await self._get_driver_data(
                start_date,
                end_date,
                [driver_id] if driver_id else None
            )

            performances = []
            for driver in drivers:
                # Calculate performance metrics
                metrics = await self._calculate_driver_metrics(driver)

                # Analyze trends
                trends = self._analyze_driver_trends(driver, metrics)

                # Generate insights
                insights = self._generate_driver_insights(metrics, trends)

                performances.append(
                    await DriverPerformance.create(
                        driver_id=driver['id'],
                        metrics=metrics,
                        trends=trends,
                        insights=insights,
                        start_date=start_date or min(metrics.keys()),
                        end_date=end_date or max(metrics.keys()),
                        created_at=datetime.now()
                    )
                )

            return performances

        except Exception as e:
            logger.error(f"Error tracking driver performance: {str(e)}")
            raise

    async def analyze_customer_satisfaction(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[CustomerMetric]:
        """
        Analyze customer satisfaction metrics
        """
        try:
            # Get customer data
            ratings = await self._get_rating_data(start_date, end_date)
            feedback = await self._get_feedback_data(start_date, end_date)
            interactions = await self._get_interaction_data(start_date, end_date)

            metrics = []
            # Calculate satisfaction metrics
            satisfaction = self._calculate_satisfaction_metrics(
                ratings,
                feedback,
                interactions
            )

            # Analyze feedback patterns
            patterns = self._analyze_feedback_patterns(feedback)

            # Identify improvement areas
            improvements = self._identify_improvement_areas(
                satisfaction,
                patterns
            )

            metrics.append(
                await CustomerMetric.create(
                    metrics=satisfaction,
                    patterns=patterns,
                    improvements=improvements,
                    start_date=start_date,
                    end_date=end_date,
                    created_at=datetime.now()
                )
            )

            return metrics

        except Exception as e:
            logger.error(f"Error analyzing customer satisfaction: {str(e)}")
            raise

    async def generate_analytics_report(
        self,
        report_type: str,
        parameters: Dict
    ) -> AnalyticsReport:
        """
        Generate comprehensive analytics report
        """
        try:
            # Get report configuration
            config = self.analysis_config.reports.get(report_type)
            if not config:
                raise ValueError(f"Invalid report type: {report_type}")

            # Gather required metrics
            metrics = await self._gather_report_metrics(
                config['metrics'],
                parameters
            )

            # Generate visualizations
            visualizations = await self._generate_visualizations(
                metrics,
                config['visualizations']
            )

            # Create insights
            insights = self._generate_report_insights(metrics)

            # Generate recommendations
            recommendations = self._generate_report_recommendations(
                metrics,
                insights
            )

            return await AnalyticsReport.create(
                report_type=report_type,
                parameters=parameters,
                metrics=metrics,
                visualizations=visualizations,
                insights=insights,
                recommendations=recommendations,
                created_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error generating analytics report: {str(e)}")
            raise

    async def _calculate_metric(
        self,
        metric_type: str,
        deliveries: List[Dict],
        routes: List[Dict],
        drivers: List[Dict]
    ) -> float:
        """
        Calculate specific performance metric
        """
        if metric_type == 'on_time_delivery_rate':
            return self._calculate_on_time_rate(deliveries)
        elif metric_type == 'average_delivery_time':
            return self._calculate_avg_delivery_time(deliveries)
        elif metric_type == 'route_efficiency':
            return self._calculate_route_efficiency(routes)
        elif metric_type == 'driver_utilization':
            return self._calculate_driver_utilization(drivers)
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")

    def _calculate_on_time_rate(self, deliveries: List[Dict]) -> float:
        """
        Calculate on-time delivery rate
        """
        if not deliveries:
            return 0.0

        on_time = sum(
            1 for d in deliveries
            if self._is_delivery_on_time(d)
        )
        return on_time / len(deliveries)

    def _calculate_avg_delivery_time(self, deliveries: List[Dict]) -> float:
        """
        Calculate average delivery time
        """
        if not deliveries:
            return 0.0

        delivery_times = [
            (d['completed_at'] - d['started_at']).total_seconds()
            for d in deliveries
            if d['completed_at'] and d['started_at']
        ]
        return np.mean(delivery_times) if delivery_times else 0.0

    def _calculate_route_efficiency(self, routes: List[Dict]) -> float:
        """
        Calculate route efficiency score
        """
        if not routes:
            return 0.0

        efficiencies = []
        for route in routes:
            planned_distance = route['planned_distance']
            actual_distance = route['actual_distance']
            if planned_distance > 0:
                efficiencies.append(planned_distance / actual_distance)

        return np.mean(efficiencies) if efficiencies else 0.0

    def _calculate_driver_utilization(self, drivers: List[Dict]) -> float:
        """
        Calculate driver utilization rate
        """
        if not drivers:
            return 0.0

        utilizations = []
        for driver in drivers:
            active_time = sum(
                (s['end_time'] - s['start_time']).total_seconds()
                for s in driver['shifts']
            )
            delivery_time = sum(
                (d['completed_at'] - d['started_at']).total_seconds()
                for d in driver['deliveries']
                if d['completed_at'] and d['started_at']
            )
            if active_time > 0:
                utilizations.append(delivery_time / active_time)

        return np.mean(utilizations) if utilizations else 0.0

    def _identify_route_opportunities(
        self,
        route: Dict,
        metrics: Dict
    ) -> List[Dict]:
        """
        Identify route optimization opportunities
        """
        opportunities = []

        # Check for high idle time
        if metrics['idle_time'] > self.analysis_config.thresholds.idle_time:
            opportunities.append({
                'type': 'idle_time',
                'severity': 'high',
                'potential_savings': self._calculate_idle_savings(
                    metrics['idle_time']
                )
            })

        # Check for route deviation
        if metrics['deviation_rate'] > self.analysis_config.thresholds.deviation:
            opportunities.append({
                'type': 'route_deviation',
                'severity': 'medium',
                'potential_savings': self._calculate_deviation_savings(
                    metrics['deviation_rate']
                )
            })

        return opportunities

    def _generate_route_recommendations(
        self,
        metrics: Dict,
        opportunities: List[Dict]
    ) -> List[str]:
        """
        Generate route optimization recommendations
        """
        recommendations = []

        for opportunity in opportunities:
            if opportunity['type'] == 'idle_time':
                recommendations.append(
                    "Reduce idle time by optimizing delivery windows"
                )
            elif opportunity['type'] == 'route_deviation':
                recommendations.append(
                    "Improve route adherence through better planning"
                )

        return recommendations

    def _analyze_driver_trends(
        self,
        driver: Dict,
        metrics: Dict
    ) -> Dict:
        """
        Analyze driver performance trends
        """
        trends = {}

        # Analyze delivery time trend
        delivery_times = [
            m['delivery_time'] for m in metrics.values()
        ]
        trends['delivery_time'] = self._calculate_trend(delivery_times)

        # Analyze customer rating trend
        ratings = [
            m['customer_rating'] for m in metrics.values()
        ]
        trends['customer_rating'] = self._calculate_trend(ratings)

        return trends

    def _calculate_trend(self, values: List[float]) -> Dict:
        """
        Calculate trend statistics
        """
        if not values:
            return {
                'direction': 'stable',
                'magnitude': 0.0
            }

        # Calculate slope
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)

        return {
            'direction': 'improving' if slope > 0 else 'declining',
            'magnitude': abs(slope)
        }

    def _calculate_satisfaction_metrics(
        self,
        ratings: List[Dict],
        feedback: List[Dict],
        interactions: List[Dict]
    ) -> Dict:
        """
        Calculate customer satisfaction metrics
        """
        metrics = {}

        # Calculate average rating
        if ratings:
            metrics['average_rating'] = np.mean([r['rating'] for r in ratings])

        # Calculate sentiment scores
        if feedback:
            metrics['sentiment_score'] = self._calculate_sentiment(feedback)

        # Calculate response rates
        if interactions:
            metrics['response_rate'] = self._calculate_response_rate(
                interactions
            )

        return metrics

    def _analyze_feedback_patterns(self, feedback: List[Dict]) -> Dict:
        """
        Analyze patterns in customer feedback
        """
        patterns = {}

        # Analyze common themes
        themes = self._extract_feedback_themes(feedback)
        patterns['common_themes'] = themes

        # Analyze feedback timing
        timing = self._analyze_feedback_timing(feedback)
        patterns['timing_patterns'] = timing

        return patterns

    def _identify_improvement_areas(
        self,
        satisfaction: Dict,
        patterns: Dict
    ) -> List[Dict]:
        """
        Identify areas for improvement
        """
        improvements = []

        # Check rating thresholds
        if satisfaction.get('average_rating', 5) < 4.0:
            improvements.append({
                'area': 'customer_satisfaction',
                'priority': 'high',
                'recommendation': 'Improve overall service quality'
            })

        # Check common themes
        for theme in patterns.get('common_themes', []):
            if theme['sentiment'] == 'negative':
                improvements.append({
                    'area': theme['category'],
                    'priority': 'medium',
                    'recommendation': f"Address issues with {theme['category']}"
                })

        return improvements
