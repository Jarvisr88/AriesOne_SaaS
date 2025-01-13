from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.core.config import config_manager
from app.core.logging import logger
from app.core.monitoring import metrics
from app.core.security import SecurityContext
from app.core.events import EventBus, Event

class IntegrationEvent(Event):
    """Base integration event"""
    def __init__(
        self,
        event_type: str,
        source: str,
        data: Dict,
        correlation_id: Optional[str] = None
    ):
        super().__init__(event_type)
        self.source = source
        self.data = data
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow()

class IntegrationMetrics:
    """Integration metrics tracking"""
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.request_count = metrics.counter(
            f"integration_{service_name}_requests_total",
            f"Total {service_name} integration requests"
        )
        self.error_count = metrics.counter(
            f"integration_{service_name}_errors_total",
            f"Total {service_name} integration errors"
        )
        self.response_time = metrics.histogram(
            f"integration_{service_name}_response_time_seconds",
            f"{service_name} integration response time"
        )
        self.active_connections = metrics.gauge(
            f"integration_{service_name}_active_connections",
            f"Active {service_name} integration connections"
        )

class IntegrationService:
    """Base integration service"""
    def __init__(
        self,
        db: Session,
        event_bus: EventBus,
        security_context: SecurityContext,
        service_name: str
    ):
        self.db = db
        self.event_bus = event_bus
        self.security_context = security_context
        self.service_name = service_name
        self.metrics = IntegrationMetrics(service_name)
        self._setup_service()

    def _setup_service(self):
        """Setup integration service"""
        raise NotImplementedError

    async def _emit_event(
        self,
        event_type: str,
        data: Dict,
        correlation_id: Optional[str] = None
    ):
        """Emit integration event"""
        event = IntegrationEvent(
            event_type=event_type,
            source=self.service_name,
            data=data,
            correlation_id=correlation_id
        )
        await self.event_bus.emit(event)

    async def _track_metrics(
        self,
        start_time: datetime,
        success: bool,
        connection_delta: int = 0
    ):
        """Track integration metrics"""
        self.metrics.request_count.inc()
        if not success:
            self.metrics.error_count.inc()
        
        response_time = (datetime.utcnow() - start_time).total_seconds()
        self.metrics.response_time.observe(response_time)
        
        if connection_delta:
            self.metrics.active_connections.inc(connection_delta)

    async def get_metrics(self) -> Dict:
        """Get integration metrics"""
        return {
            "request_count": self.metrics.request_count._value.get(),
            "error_count": self.metrics.error_count._value.get(),
            "response_time": self.metrics.response_time._value.get(),
            "active_connections": self.metrics.active_connections._value.get()
        }

class DatabaseIntegration(IntegrationService):
    """Database integration service"""
    def _setup_service(self):
        """Setup database connection pool"""
        self.pool_size = config_manager.get("DB_POOL_SIZE", 10)
        self.max_overflow = config_manager.get("DB_MAX_OVERFLOW", 20)
        self.pool_timeout = config_manager.get("DB_POOL_TIMEOUT", 30)
        
        # Update active connections
        self.metrics.active_connections.set(self.pool_size)

    async def execute_query(
        self,
        query: str,
        params: Optional[Dict] = None,
        correlation_id: Optional[str] = None
    ) -> List[Dict]:
        """Execute database query"""
        start_time = datetime.utcnow()
        success = False
        
        try:
            # Track connection
            await self._track_metrics(start_time, True, 1)
            
            # Execute query
            result = self.db.execute(query, params or {})
            rows = [dict(row) for row in result]
            
            # Emit event
            await self._emit_event(
                "query_executed",
                {
                    "query": query,
                    "params": params,
                    "row_count": len(rows)
                },
                correlation_id
            )
            
            success = True
            return rows
            
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            await self._emit_event(
                "query_error",
                {
                    "query": query,
                    "params": params,
                    "error": str(e)
                },
                correlation_id
            )
            raise
            
        finally:
            # Track metrics
            await self._track_metrics(start_time, success, -1)

class SecurityIntegration(IntegrationService):
    """Security integration service"""
    def _setup_service(self):
        """Setup security service"""
        self.token_expiry = config_manager.get("TOKEN_EXPIRY", 3600)
        self.max_attempts = config_manager.get("MAX_LOGIN_ATTEMPTS", 3)
        self.lockout_time = config_manager.get("ACCOUNT_LOCKOUT_TIME", 300)

    async def authenticate(
        self,
        credentials: Dict,
        correlation_id: Optional[str] = None
    ) -> Dict:
        """Authenticate user"""
        start_time = datetime.utcnow()
        success = False
        
        try:
            # Validate credentials
            token = await self.security_context.authenticate(
                credentials["username"],
                credentials["password"]
            )
            
            # Emit event
            await self._emit_event(
                "user_authenticated",
                {
                    "username": credentials["username"],
                    "token_expiry": self.token_expiry
                },
                correlation_id
            )
            
            success = True
            return {
                "token": token,
                "expiry": self.token_expiry
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            await self._emit_event(
                "authentication_error",
                {
                    "username": credentials["username"],
                    "error": str(e)
                },
                correlation_id
            )
            raise
            
        finally:
            # Track metrics
            await self._track_metrics(start_time, success)

class AnalyticsIntegration(IntegrationService):
    """Analytics integration service"""
    def _setup_service(self):
        """Setup analytics service"""
        self.batch_size = config_manager.get("ANALYTICS_BATCH_SIZE", 100)
        self.flush_interval = config_manager.get("ANALYTICS_FLUSH_INTERVAL", 60)
        self.event_buffer: List[Dict] = []
        self._setup_flush_task()

    def _setup_flush_task(self):
        """Setup periodic flush task"""
        asyncio.create_task(self._periodic_flush())

    async def _periodic_flush(self):
        """Periodically flush events"""
        while True:
            await asyncio.sleep(self.flush_interval)
            if self.event_buffer:
                await self.flush_events()

    async def track_event(
        self,
        event_type: str,
        event_data: Dict,
        correlation_id: Optional[str] = None
    ):
        """Track analytics event"""
        start_time = datetime.utcnow()
        
        try:
            # Add event to buffer
            self.event_buffer.append({
                "type": event_type,
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat(),
                "correlation_id": correlation_id
            })
            
            # Flush if batch size reached
            if len(self.event_buffer) >= self.batch_size:
                await self.flush_events()
                
        except Exception as e:
            logger.error(f"Event tracking error: {e}")
            await self._track_metrics(start_time, False)
            raise

    async def flush_events(self):
        """Flush buffered events"""
        if not self.event_buffer:
            return
            
        start_time = datetime.utcnow()
        success = False
        
        try:
            # Process events
            events = self.event_buffer
            self.event_buffer = []
            
            # Emit event
            await self._emit_event(
                "events_flushed",
                {
                    "event_count": len(events),
                    "events": events
                }
            )
            
            success = True
            
        except Exception as e:
            logger.error(f"Event flush error: {e}")
            # Restore events to buffer
            self.event_buffer.extend(events)
            raise
            
        finally:
            # Track metrics
            await self._track_metrics(start_time, success)

# Create integration service factories
def get_database_integration(
    db: Session,
    event_bus: EventBus,
    security_context: SecurityContext
) -> DatabaseIntegration:
    return DatabaseIntegration(db, event_bus, security_context, "database")

def get_security_integration(
    db: Session,
    event_bus: EventBus,
    security_context: SecurityContext
) -> SecurityIntegration:
    return SecurityIntegration(db, event_bus, security_context, "security")

def get_analytics_integration(
    db: Session,
    event_bus: EventBus,
    security_context: SecurityContext
) -> AnalyticsIntegration:
    return AnalyticsIntegration(db, event_bus, security_context, "analytics")
