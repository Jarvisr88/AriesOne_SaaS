"""
Event Bus Integration Tests
Version: 1.0.0
Last Updated: 2025-01-10
"""
import asyncio
from datetime import datetime
from typing import Dict, List

import pytest
from aio_pika import connect_robust

from core.integrations.event_bus import Event, EventBusIntegration
from core.utils.config import get_settings

settings = get_settings()


@pytest.fixture
async def event_bus():
    """Create event bus integration instance."""
    bus = EventBusIntegration()
    await bus.connect()
    yield bus
    await bus.disconnect()


@pytest.fixture
def test_event():
    """Create test event."""
    return Event(
        event_type="test_event",
        payload={"test": "data"},
        source="test"
    )


@pytest.mark.asyncio
async def test_connect_disconnect(event_bus):
    """Test connection and disconnection."""
    assert event_bus._connection is not None
    assert event_bus._channel is not None
    assert event_bus._exchange is not None
    
    await event_bus.disconnect()
    assert event_bus._connection is None
    assert event_bus._channel is None
    assert event_bus._exchange is None


@pytest.mark.asyncio
async def test_publish_subscribe(event_bus, test_event):
    """Test event publishing and subscribing."""
    received_events: List[Event] = []
    
    async def handle_event(event: Event):
        received_events.append(event)
    
    # Subscribe to test events
    await event_bus.subscribe("test.#", handle_event)
    
    # Publish test event
    await event_bus.publish(test_event, "test.event")
    
    # Wait for event processing
    await asyncio.sleep(1)
    
    assert len(received_events) == 1
    received = received_events[0]
    assert received.type == test_event.type
    assert received.payload == test_event.payload
    assert received.source == test_event.source


@pytest.mark.asyncio
async def test_multiple_subscribers(event_bus, test_event):
    """Test multiple subscribers for same event."""
    received_events_1: List[Event] = []
    received_events_2: List[Event] = []
    
    async def handle_event_1(event: Event):
        received_events_1.append(event)
    
    async def handle_event_2(event: Event):
        received_events_2.append(event)
    
    # Subscribe both handlers
    await event_bus.subscribe("test.#", handle_event_1)
    await event_bus.subscribe("test.#", handle_event_2)
    
    # Publish test event
    await event_bus.publish(test_event, "test.event")
    
    # Wait for event processing
    await asyncio.sleep(1)
    
    assert len(received_events_1) == 1
    assert len(received_events_2) == 1
    assert received_events_1[0].id == received_events_2[0].id


@pytest.mark.asyncio
async def test_unsubscribe(event_bus, test_event):
    """Test unsubscribing from events."""
    received_events: List[Event] = []
    
    async def handle_event(event: Event):
        received_events.append(event)
    
    # Subscribe and then unsubscribe
    await event_bus.subscribe("test.#", handle_event)
    await event_bus.unsubscribe("test.#", handle_event)
    
    # Publish test event
    await event_bus.publish(test_event, "test.event")
    
    # Wait for event processing
    await asyncio.sleep(1)
    
    assert len(received_events) == 0


@pytest.mark.asyncio
async def test_event_routing(event_bus):
    """Test event routing patterns."""
    received_events: Dict[str, List[Event]] = {
        "all": [],
        "specific": []
    }
    
    async def handle_all(event: Event):
        received_events["all"].append(event)
    
    async def handle_specific(event: Event):
        received_events["specific"].append(event)
    
    # Subscribe with different patterns
    await event_bus.subscribe("#", handle_all)
    await event_bus.subscribe("test.specific.#", handle_specific)
    
    # Publish events with different routing keys
    events = [
        (Event("test1", {}, "test"), "test.general"),
        (Event("test2", {}, "test"), "test.specific.event"),
        (Event("test3", {}, "test"), "other.event")
    ]
    
    for event, routing_key in events:
        await event_bus.publish(event, routing_key)
    
    # Wait for event processing
    await asyncio.sleep(1)
    
    assert len(received_events["all"]) == 3
    assert len(received_events["specific"]) == 1
    assert received_events["specific"][0].type == "test2"


@pytest.mark.asyncio
async def test_health_check(event_bus):
    """Test health check functionality."""
    # Test when connected
    health = await event_bus.health_check()
    assert health["status"] == "healthy"
    
    # Test when disconnected
    await event_bus.disconnect()
    health = await event_bus.health_check()
    assert health["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_event_serialization(test_event):
    """Test event serialization/deserialization."""
    # Convert to dict
    event_dict = test_event.to_dict()
    assert isinstance(event_dict["id"], str)
    assert isinstance(event_dict["timestamp"], str)
    assert event_dict["type"] == test_event.type
    assert event_dict["payload"] == test_event.payload
    assert event_dict["source"] == test_event.source
    
    # Convert back to event
    recreated_event = Event.from_dict(event_dict)
    assert recreated_event.id == test_event.id
    assert recreated_event.type == test_event.type
    assert recreated_event.payload == test_event.payload
    assert recreated_event.source == test_event.source
    assert recreated_event.timestamp == test_event.timestamp
