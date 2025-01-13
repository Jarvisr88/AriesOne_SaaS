"""FastAPI dependency injection module."""
from typing import AsyncGenerator, Callable
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.session import async_session
from infrastructure.data.unit_of_work import UnitOfWork
from infrastructure.caching.redis_cache import RedisCache, RedisCacheSettings
from infrastructure.messaging.kafka_bus import KafkaEventBus, KafkaSettings
from infrastructure.messaging.rabbitmq_queue import MessageQueue, RabbitMQSettings
from core.security.encryption import EncryptionService, EncryptionSettings
from core.security.audit import AuditService

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session.
    
    Yields:
        Database session.
    """
    async with async_session() as session:
        yield session

async def get_unit_of_work(
    session: AsyncSession = Depends(get_db)
) -> UnitOfWork:
    """Get unit of work.
    
    Args:
        session: Database session.
        
    Returns:
        Unit of work.
    """
    return UnitOfWork(session)

def get_cache(settings: RedisCacheSettings = Depends(RedisCacheSettings)) -> RedisCache:
    """Get cache service.
    
    Args:
        settings: Redis settings.
        
    Returns:
        Cache service.
    """
    return RedisCache(settings)

def get_event_bus(
    settings: KafkaSettings = Depends(KafkaSettings)
) -> KafkaEventBus:
    """Get event bus.
    
    Args:
        settings: Kafka settings.
        
    Returns:
        Event bus.
    """
    return KafkaEventBus(settings)

def get_message_queue(
    settings: RabbitMQSettings = Depends(RabbitMQSettings)
) -> MessageQueue:
    """Get message queue.
    
    Args:
        settings: RabbitMQ settings.
        
    Returns:
        Message queue.
    """
    return MessageQueue(settings)

def get_encryption_service(
    settings: EncryptionSettings = Depends(EncryptionSettings)
) -> EncryptionService:
    """Get encryption service.
    
    Args:
        settings: Encryption settings.
        
    Returns:
        Encryption service.
    """
    return EncryptionService(settings)

def get_audit_service(
    session_factory: Callable = Depends(get_db)
) -> AuditService:
    """Get audit service.
    
    Args:
        session_factory: Database session factory.
        
    Returns:
        Audit service.
    """
    return AuditService(session_factory)

def get_current_user(request: Request) -> dict:
    """Get current user from request state.
    
    Args:
        request: HTTP request.
        
    Returns:
        User information.
    """
    return {
        "id": request.state.user_id,
        "roles": request.state.user_roles
    }
