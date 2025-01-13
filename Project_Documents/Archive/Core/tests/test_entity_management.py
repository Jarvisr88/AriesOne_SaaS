"""
Integration tests for entity management service.
"""
import pytest
from uuid import UUID
from httpx import AsyncClient

from ..services.entity_management_service import EntityManagementService
from ..models.entity import EntityCreatedEvent

@pytest.mark.asyncio
async def test_create_entity(client: AsyncClient, db_session):
    """Test entity creation"""
    service = EntityManagementService()
    
    # Test data
    entity_data = {
        "entity_type": "test_entity",
        "data": {"name": "Test Entity", "value": 123},
        "metadata": {"created_by": "test_user"}
    }
    
    # Create entity
    event = await service.create_entity(
        entity_type=entity_data["entity_type"],
        data=entity_data["data"],
        metadata=entity_data["metadata"]
    )
    
    # Verify event
    assert isinstance(event, EntityCreatedEvent)
    assert isinstance(event.entity_id, UUID)
    assert event.entity_type == entity_data["entity_type"]
    assert event.data == entity_data["data"]
    assert event.metadata == entity_data["metadata"]

@pytest.mark.asyncio
async def test_entity_listener(client: AsyncClient, db_session):
    """Test entity creation event listener"""
    service = EntityManagementService()
    received_events = []
    
    # Create test listener
    class TestListener:
        async def on_entity_created(self, event: EntityCreatedEvent):
            received_events.append(event)
    
    # Register listener
    listener = TestListener()
    await service.register_entity_listener("test_entity", listener)
    
    # Create entity
    entity_data = {
        "entity_type": "test_entity",
        "data": {"name": "Test Entity"},
        "metadata": {}
    }
    
    event = await service.create_entity(
        entity_type=entity_data["entity_type"],
        data=entity_data["data"],
        metadata=entity_data["metadata"]
    )
    
    # Verify listener received event
    assert len(received_events) == 1
    received = received_events[0]
    assert received.entity_id == event.entity_id
    assert received.entity_type == event.entity_type
    assert received.data == event.data
    
    # Unregister listener
    await service.unregister_entity_listener("test_entity", listener)
    
    # Create another entity
    await service.create_entity(
        entity_type=entity_data["entity_type"],
        data=entity_data["data"],
        metadata=entity_data["metadata"]
    )
    
    # Verify no new events received
    assert len(received_events) == 1
