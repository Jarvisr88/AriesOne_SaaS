"""
Core Event Bus Integration Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides event bus integration functionality.
"""
import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4

import aio_pika
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage

from ..utils.config import get_settings
from ..utils.logging import CoreLogger

settings = get_settings()
logger = CoreLogger(__name__)


class Event:
    """Event model."""
    
    def __init__(self, event_type: str, payload: Dict[str, Any],
                 source: str = "core"):
        """Initialize event."""
        self.id = uuid4()
        self.type = event_type
        self.payload = payload
        self.source = source
        self.timestamp = datetime.utcnow()
        self.version = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": str(self.id),
            "type": self.type,
            "payload": self.payload,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        event = cls(data["type"], data["payload"], data["source"])
        event.id = UUID(data["id"])
        event.timestamp = datetime.fromisoformat(data["timestamp"])
        event.version = data["version"]
        return event


class EventBusIntegration:
    """Event bus integration service."""
    
    def __init__(self):
        """Initialize event bus integration."""
        self._connection = None
        self._channel = None
        self._exchange = None
        self._subscribers: Dict[str, List[Callable]] = {}
    
    async def connect(self) -> None:
        """Connect to event bus."""
        try:
            self._connection = await connect_robust(
                host=settings.EVENT_STORE_URL,
                port=5672,  # Default RabbitMQ port
                login="guest",  # Configure in production
                password="guest"  # Configure in production
            )
            
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                "core_events",
                aio_pika.ExchangeType.TOPIC
            )
            
            logger.info("Connected to event bus")
        except Exception as e:
            logger.error(f"Failed to connect to event bus: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from event bus."""
        try:
            if self._connection:
                await self._connection.close()
                self._connection = None
                self._channel = None
                self._exchange = None
                logger.info("Disconnected from event bus")
        except Exception as e:
            logger.error(f"Failed to disconnect from event bus: {str(e)}")
            raise
    
    async def publish(self, event: Event, routing_key: str) -> None:
        """Publish event to event bus."""
        try:
            if not self._exchange:
                await self.connect()
            
            message = Message(
                body=json.dumps(event.to_dict()).encode(),
                content_type="application/json",
                message_id=str(event.id),
                timestamp=int(event.timestamp.timestamp())
            )
            
            await self._exchange.publish(message, routing_key=routing_key)
            logger.info(f"Published event {event.id} with routing key {routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
            raise
    
    async def subscribe(self, routing_key: str,
                       callback: Callable[[Event], None]) -> None:
        """Subscribe to events with routing key."""
        try:
            if not self._channel:
                await self.connect()
            
            # Create queue with unique name
            queue = await self._channel.declare_queue(exclusive=True)
            await queue.bind(self._exchange, routing_key=routing_key)
            
            # Store callback
            if routing_key not in self._subscribers:
                self._subscribers[routing_key] = []
            self._subscribers[routing_key].append(callback)
            
            async def process_message(message: AbstractIncomingMessage) -> None:
                """Process received message."""
                async with message.process():
                    try:
                        event_data = json.loads(message.body.decode())
                        event = Event.from_dict(event_data)
                        
                        # Call all subscribers
                        for cb in self._subscribers[routing_key]:
                            await cb(event)
                    except Exception as e:
                        logger.error(f"Failed to process message: {str(e)}")
            
            # Start consuming messages
            await queue.consume(process_message)
            logger.info(f"Subscribed to events with routing key {routing_key}")
        except Exception as e:
            logger.error(f"Failed to subscribe to events: {str(e)}")
            raise
    
    async def unsubscribe(self, routing_key: str,
                         callback: Optional[Callable] = None) -> None:
        """Unsubscribe from events."""
        try:
            if routing_key in self._subscribers:
                if callback:
                    self._subscribers[routing_key].remove(callback)
                    if not self._subscribers[routing_key]:
                        del self._subscribers[routing_key]
                else:
                    del self._subscribers[routing_key]
                
                logger.info(f"Unsubscribed from events with routing key {routing_key}")
        except Exception as e:
            logger.error(f"Failed to unsubscribe from events: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, str]:
        """Check event bus health."""
        try:
            if not self._connection or self._connection.is_closed:
                return {
                    "status": "unhealthy",
                    "message": "Not connected to event bus"
                }
            
            return {
                "status": "healthy",
                "message": "Connected to event bus"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": str(e)
            }


# Global event bus instance
_event_bus: Optional[EventBusIntegration] = None


async def get_event_bus() -> EventBusIntegration:
    """Get event bus instance."""
    global _event_bus
    if not _event_bus:
        _event_bus = EventBusIntegration()
        await _event_bus.connect()
    return _event_bus
