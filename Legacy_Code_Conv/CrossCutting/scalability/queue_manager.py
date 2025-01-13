"""Queue management module."""

import json
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime
import asyncio
import aio_pika
from aio_pika.pool import Pool
from app.core.config import settings

class QueueManager:
    """Manager for message queues."""
    
    def __init__(self):
        """Initialize queue manager."""
        self.connection_pool: Optional[Pool] = None
        self.channel_pool: Optional[Pool] = None
        self._consumers: Dict[str, List[Callable]] = {}
    
    async def connect(self) -> None:
        """Connect to message broker."""
        # Create connection pool
        self.connection_pool = Pool(
            self._get_connection,
            max_size=settings.QUEUE_POOL_SIZE
        )
        
        # Create channel pool
        self.channel_pool = Pool(
            self._get_channel,
            max_size=settings.QUEUE_POOL_SIZE
        )
    
    async def _get_connection(self) -> aio_pika.Connection:
        """Get connection from pool."""
        return await aio_pika.connect_robust(
            settings.RABBITMQ_URL,
            loop=asyncio.get_event_loop()
        )
    
    async def _get_channel(self) -> aio_pika.Channel:
        """Get channel from pool."""
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()
    
    async def publish(
        self,
        queue_name: str,
        message: Dict[str, Any],
        priority: int = 0,
        delay: Optional[int] = None
    ) -> None:
        """Publish message to queue."""
        # Add metadata
        message['_metadata'] = {
            'timestamp': datetime.utcnow().isoformat(),
            'priority': priority
        }
        
        # Create message
        body = json.dumps(message).encode()
        message = aio_pika.Message(
            body=body,
            priority=priority,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        async with self.channel_pool.acquire() as channel:
            # Declare queue
            queue = await channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    'x-max-priority': 10
                }
            )
            
            # Handle delayed messages
            if delay:
                delayed_exchange = await channel.declare_exchange(
                    'delayed',
                    aio_pika.ExchangeType.X_DELAYED_MESSAGE,
                    arguments={
                        'x-delayed-type': 'direct'
                    }
                )
                
                message.headers['x-delay'] = delay * 1000
                await delayed_exchange.publish(
                    message,
                    routing_key=queue_name
                )
            else:
                # Publish directly to queue
                await channel.default_exchange.publish(
                    message,
                    routing_key=queue_name
                )
    
    async def subscribe(
        self,
        queue_name: str,
        callback: Callable,
        prefetch_count: int = 10
    ) -> None:
        """Subscribe to queue."""
        if queue_name not in self._consumers:
            self._consumers[queue_name] = []
        
        self._consumers[queue_name].append(callback)
        
        async with self.channel_pool.acquire() as channel:
            # Set prefetch count
            await channel.set_qos(prefetch_count=prefetch_count)
            
            # Declare queue
            queue = await channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    'x-max-priority': 10
                }
            )
            
            # Start consuming
            await queue.consume(self._message_handler)
    
    async def _message_handler(
        self,
        message: aio_pika.IncomingMessage
    ) -> None:
        """Handle incoming message."""
        async with message.process():
            try:
                # Parse message
                body = json.loads(message.body.decode())
                queue_name = message.routing_key
                
                # Call all registered callbacks
                if queue_name in self._consumers:
                    for callback in self._consumers[queue_name]:
                        try:
                            await callback(body)
                        except Exception as e:
                            # Log error but don't stop processing
                            print(f"Error in callback: {str(e)}")
            except json.JSONDecodeError:
                print("Invalid message format")
            except Exception as e:
                print(f"Error processing message: {str(e)}")
    
    async def close(self) -> None:
        """Close all connections."""
        if self.channel_pool:
            await self.channel_pool.close()
        if self.connection_pool:
            await self.connection_pool.close()

class QueueMonitor:
    """Monitor for queue metrics."""
    
    def __init__(self, queue_manager: QueueManager):
        """Initialize queue monitor."""
        self.queue_manager = queue_manager
        self.metrics: Dict[str, Dict[str, int]] = {}
    
    async def update_metrics(self) -> None:
        """Update queue metrics."""
        async with self.queue_manager.channel_pool.acquire() as channel:
            for queue_name in self.queue_manager._consumers.keys():
                queue = await channel.declare_queue(
                    queue_name,
                    durable=True,
                    passive=True
                )
                
                self.metrics[queue_name] = {
                    'message_count': queue.declaration_result.message_count,
                    'consumer_count': queue.declaration_result.consumer_count
                }
    
    def get_metrics(self) -> Dict[str, Dict[str, int]]:
        """Get queue metrics."""
        return self.metrics.copy()
