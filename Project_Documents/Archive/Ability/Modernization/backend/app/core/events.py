from typing import Dict, List, Optional, Callable, Awaitable, Any
import asyncio
from datetime import datetime
import uuid
from app.core.logging import logger
from app.core.monitoring import metrics

class Event:
    """Base event class"""
    def __init__(self, event_type: str):
        self.event_type = event_type
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()

class EventHandler:
    """Event handler class"""
    def __init__(
        self,
        handler_id: str,
        callback: Callable[[Event], Awaitable[None]]
    ):
        self.handler_id = handler_id
        self.callback = callback

class EventMetrics:
    """Event metrics tracking"""
    def __init__(self):
        self.event_count = metrics.counter(
            "events_total",
            "Total number of events"
        )
        self.handler_count = metrics.counter(
            "event_handlers_total",
            "Total number of event handlers"
        )
        self.processing_time = metrics.histogram(
            "event_processing_time_seconds",
            "Event processing time"
        )
        self.error_count = metrics.counter(
            "event_errors_total",
            "Total number of event processing errors"
        )

class EventBus:
    """Event bus implementation"""
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._metrics = EventMetrics()
        self._setup_metrics()

    def _setup_metrics(self):
        """Setup event metrics"""
        # Track total handlers
        total_handlers = sum(len(handlers) for handlers in self._handlers.values())
        self._metrics.handler_count.inc(total_handlers)

    async def emit(self, event: Event):
        """Emit event to all registered handlers"""
        start_time = datetime.utcnow()
        
        try:
            # Track event
            self._metrics.event_count.inc()
            
            # Get handlers
            handlers = self._handlers.get(event.event_type, [])
            if not handlers:
                return
            
            # Process event
            tasks = [
                self._process_handler(handler, event)
                for handler in handlers
            ]
            await asyncio.gather(*tasks)
            
            # Track processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._metrics.processing_time.observe(processing_time)
            
        except Exception as e:
            logger.error(f"Event processing error: {e}")
            self._metrics.error_count.inc()
            raise

    async def _process_handler(
        self,
        handler: EventHandler,
        event: Event
    ):
        """Process event with handler"""
        try:
            await handler.callback(event)
        except Exception as e:
            logger.error(
                f"Handler {handler.handler_id} error "
                f"for event {event.event_type}: {e}"
            )
            self._metrics.error_count.inc()

    def subscribe(
        self,
        event_type: str,
        handler_id: str,
        callback: Callable[[Event], Awaitable[None]]
    ):
        """Subscribe to event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
            
        # Create handler
        handler = EventHandler(handler_id, callback)
        self._handlers[event_type].append(handler)
        
        # Track handler
        self._metrics.handler_count.inc()

    def unsubscribe(
        self,
        event_type: str,
        handler_id: str
    ):
        """Unsubscribe from event type"""
        if event_type not in self._handlers:
            return
            
        # Remove handler
        self._handlers[event_type] = [
            h for h in self._handlers[event_type]
            if h.handler_id != handler_id
        ]
        
        # Track handler removal
        self._metrics.handler_count.dec()

    async def get_metrics(self) -> Dict:
        """Get event metrics"""
        return {
            "event_count": self._metrics.event_count._value.get(),
            "handler_count": self._metrics.handler_count._value.get(),
            "processing_time": self._metrics.processing_time._value.get(),
            "error_count": self._metrics.error_count._value.get()
        }

# Create event bus instance
event_bus = EventBus()
