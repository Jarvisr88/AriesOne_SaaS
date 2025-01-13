from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel
from prometheus_client import Counter, Histogram
import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class AnalyticsEvent(Base):
    __tablename__ = 'analytics_events'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    event_type = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    component = Column(String, nullable=False)
    action = Column(String, nullable=False)
    data = Column(JSON, nullable=True)

class UserAction(BaseModel):
    timestamp: datetime
    user_id: Optional[str]
    component: str
    action: str
    data: Optional[Dict] = None

class ComponentUsage(BaseModel):
    component: str
    total_actions: int
    unique_users: int
    average_duration: float
    error_rate: float

class AnalyticsService:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Prometheus metrics
        self.action_counter = Counter(
            'user_actions_total',
            'Total number of user actions',
            ['component', 'action']
        )
        self.action_duration = Histogram(
            'user_action_duration_seconds',
            'Duration of user actions',
            ['component', 'action']
        )

    def track_action(self, action: UserAction):
        """Track a user action"""
        try:
            # Store in database
            session = self.Session()
            event = AnalyticsEvent(
                timestamp=action.timestamp,
                event_type="user_action",
                user_id=action.user_id,
                component=action.component,
                action=action.action,
                data=action.data
            )
            session.add(event)
            session.commit()

            # Update Prometheus metrics
            self.action_counter.labels(
                component=action.component,
                action=action.action
            ).inc()

            if action.data and "duration" in action.data:
                self.action_duration.labels(
                    component=action.component,
                    action=action.action
                ).observe(action.data["duration"])

            logger.info(f"Tracked action: {action.component} - {action.action}")
        except Exception as e:
            logger.error(f"Failed to track action: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    def get_component_usage(
        self,
        component: str,
        start_time: datetime,
        end_time: datetime
    ) -> ComponentUsage:
        """Get usage statistics for a component"""
        try:
            session = self.Session()
            
            # Get total actions
            total_actions = session.query(AnalyticsEvent).filter(
                AnalyticsEvent.component == component,
                AnalyticsEvent.timestamp.between(start_time, end_time)
            ).count()

            # Get unique users
            unique_users = session.query(AnalyticsEvent.user_id).filter(
                AnalyticsEvent.component == component,
                AnalyticsEvent.timestamp.between(start_time, end_time),
                AnalyticsEvent.user_id.isnot(None)
            ).distinct().count()

            # Calculate average duration
            events = session.query(AnalyticsEvent).filter(
                AnalyticsEvent.component == component,
                AnalyticsEvent.timestamp.between(start_time, end_time),
                AnalyticsEvent.data.contains({"duration": True})
            ).all()

            total_duration = sum(
                event.data.get("duration", 0)
                for event in events
                if event.data
            )
            avg_duration = total_duration / len(events) if events else 0

            # Calculate error rate
            error_events = session.query(AnalyticsEvent).filter(
                AnalyticsEvent.component == component,
                AnalyticsEvent.timestamp.between(start_time, end_time),
                AnalyticsEvent.action == "error"
            ).count()
            error_rate = error_events / total_actions if total_actions > 0 else 0

            return ComponentUsage(
                component=component,
                total_actions=total_actions,
                unique_users=unique_users,
                average_duration=avg_duration,
                error_rate=error_rate
            )
        finally:
            session.close()

    def get_user_journey(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[UserAction]:
        """Get the sequence of actions for a user"""
        try:
            session = self.Session()
            events = session.query(AnalyticsEvent).filter(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.timestamp.between(start_time, end_time)
            ).order_by(AnalyticsEvent.timestamp).all()

            return [
                UserAction(
                    timestamp=event.timestamp,
                    user_id=event.user_id,
                    component=event.component,
                    action=event.action,
                    data=event.data
                )
                for event in events
            ]
        finally:
            session.close()

    def export_analytics(
        self,
        start_time: datetime,
        end_time: datetime,
        format: str = 'json'
    ) -> str:
        """Export analytics data in specified format"""
        try:
            session = self.Session()
            events = session.query(AnalyticsEvent).filter(
                AnalyticsEvent.timestamp.between(start_time, end_time)
            ).order_by(AnalyticsEvent.timestamp).all()

            if format.lower() == 'json':
                return json.dumps([{
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type,
                    'user_id': event.user_id,
                    'component': event.component,
                    'action': event.action,
                    'data': event.data
                } for event in events], indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
        finally:
            session.close()

# Initialize analytics service
analytics_service = AnalyticsService("postgresql://user:password@localhost/analytics_db")
