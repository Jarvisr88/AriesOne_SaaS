"""
Database Change Service Module

This module provides services for handling database changes and notifications.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Type, Union
from uuid import UUID, uuid4
from fastapi import HTTPException
from functools import wraps
import inspect
from pydantic import BaseModel

class DatabaseChangeMetadata(BaseModel):
    """Metadata for database changes"""
    entity_type: str
    entity_id: Union[str, int, UUID]
    operation: str  # CREATE, UPDATE, DELETE
    timestamp: datetime
    user_id: Optional[UUID]
    changes: Dict[str, Any]

class DatabaseChangeSubscription(BaseModel):
    """Database change subscription"""
    subscription_id: UUID
    entity_type: str
    callback: str  # Fully qualified function name
    filters: Optional[Dict[str, Any]]
    created_at: datetime
    metadata: Dict[str, Any]

class DatabaseChangeService:
    """Service for handling database changes"""
    
    def __init__(self):
        """Initialize database change service"""
        self._subscriptions: Dict[UUID, DatabaseChangeSubscription] = {}
        self._handlers: Dict[str, List[callable]] = {}
    
    def handle_database_change(self, target_class: Optional[Type] = None):
        """
        Decorator for handling database changes.
        
        Args:
            target_class: Optional target class to monitor
            
        Returns:
            Decorator function
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get entity type
                entity_type = target_class.__name__ if target_class else func.__qualname__
                
                # Create change metadata
                metadata = DatabaseChangeMetadata(
                    entity_type=entity_type,
                    entity_id=kwargs.get('id') or args[1] if len(args) > 1 else None,
                    operation=func.__name__.upper(),
                    timestamp=datetime.utcnow(),
                    user_id=kwargs.get('user_id'),
                    changes=kwargs
                )
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Notify subscribers
                await self._notify_subscribers(metadata)
                
                return result
            return wrapper
        return decorator
    
    async def subscribe(
        self,
        entity_type: str,
        callback: callable,
        filters: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """
        Subscribe to database changes.
        
        Args:
            entity_type: Entity type to monitor
            callback: Callback function
            filters: Optional filters
            
        Returns:
            Subscription ID
        """
        subscription_id = uuid4()
        
        # Create subscription
        subscription = DatabaseChangeSubscription(
            subscription_id=subscription_id,
            entity_type=entity_type,
            callback=f"{callback.__module__}.{callback.__qualname__}",
            filters=filters,
            created_at=datetime.utcnow(),
            metadata={}
        )
        
        # Store subscription
        self._subscriptions[subscription_id] = subscription
        
        # Register handler
        if entity_type not in self._handlers:
            self._handlers[entity_type] = []
        self._handlers[entity_type].append(callback)
        
        return subscription_id
    
    async def unsubscribe(
        self,
        subscription_id: UUID
    ):
        """
        Unsubscribe from database changes.
        
        Args:
            subscription_id: Subscription ID
            
        Raises:
            HTTPException: If subscription not found
        """
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=404,
                detail=f"Subscription not found: {subscription_id}"
            )
        
        # Remove handler
        entity_type = subscription.entity_type
        if entity_type in self._handlers:
            # Get callback function
            module_name, func_name = subscription.callback.rsplit('.', 1)
            module = __import__(module_name, fromlist=[func_name])
            callback = getattr(module, func_name)
            
            if callback in self._handlers[entity_type]:
                self._handlers[entity_type].remove(callback)
        
        # Remove subscription
        del self._subscriptions[subscription_id]
    
    async def _notify_subscribers(
        self,
        metadata: DatabaseChangeMetadata
    ):
        """
        Notify subscribers of database changes.
        
        Args:
            metadata: Change metadata
        """
        entity_type = metadata.entity_type
        if entity_type in self._handlers:
            for handler in self._handlers[entity_type]:
                # Check filters
                subscription = next(
                    (s for s in self._subscriptions.values() 
                     if s.callback == f"{handler.__module__}.{handler.__qualname__}"),
                    None
                )
                
                if subscription and subscription.filters:
                    # Apply filters
                    matches = all(
                        metadata.changes.get(k) == v 
                        for k, v in subscription.filters.items()
                    )
                    if not matches:
                        continue
                
                # Call handler
                try:
                    await handler(metadata)
                except Exception as e:
                    # Log error but continue notifying other handlers
                    print(f"Error in database change handler: {e}")
                    continue
    
    def get_subscriptions(
        self,
        entity_type: Optional[str] = None
    ) -> List[DatabaseChangeSubscription]:
        """
        Get database change subscriptions.
        
        Args:
            entity_type: Optional entity type filter
            
        Returns:
            List of subscriptions
        """
        if entity_type:
            return [
                s for s in self._subscriptions.values()
                if s.entity_type == entity_type
            ]
        return list(self._subscriptions.values())
