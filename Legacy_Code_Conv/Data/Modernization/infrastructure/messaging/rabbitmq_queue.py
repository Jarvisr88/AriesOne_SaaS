"""RabbitMQ message queue implementation."""
from typing import Any, Callable, Dict, Optional
import json
import aio_pika
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage
from pydantic import BaseModel

class RabbitMQSettings(BaseModel):
    """RabbitMQ connection settings."""
    
    HOST: str = "localhost"
    PORT: int = 5672
    USERNAME: str = "guest"
    PASSWORD: str = "guest"
    VHOST: str = "/"
    CONNECTION_NAME: str = "ariesone_app"

class MessageQueue:
    """RabbitMQ message queue implementation."""

    def __init__(self, settings: RabbitMQSettings):
        """Initialize message queue.
        
        Args:
            settings: RabbitMQ connection settings.
        """
        self.settings = settings
        self._connection = None
        self._channel = None
        self._exchange = None
        self._queues: Dict[str, aio_pika.Queue] = {}

    async def connect(self) -> None:
        """Connect to RabbitMQ."""
        if not self._connection:
            self._connection = await connect_robust(
                host=self.settings.HOST,
                port=self.settings.PORT,
                login=self.settings.USERNAME,
                password=self.settings.PASSWORD,
                virtualhost=self.settings.VHOST,
                client_properties={"connection_name": self.settings.CONNECTION_NAME}
            )
            
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                "ariesone",
                aio_pika.ExchangeType.TOPIC
            )

    async def close(self) -> None:
        """Close connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._channel = None
            self._exchange = None
            self._queues = {}

    async def publish(
        self,
        routing_key: str,
        message: Dict[str, Any],
        priority: Optional[int] = None,
        expiration: Optional[int] = None
    ) -> None:
        """Publish message.
        
        Args:
            routing_key: Message routing key.
            message: Message content.
            priority: Optional message priority.
            expiration: Optional message expiration in seconds.
        """
        if not self._exchange:
            await self.connect()
        
        await self._exchange.publish(
            Message(
                body=json.dumps(message).encode(),
                content_type="application/json",
                priority=priority,
                expiration=expiration * 1000 if expiration else None
            ),
            routing_key=routing_key
        )

    async def subscribe(
        self,
        queue_name: str,
        routing_key: str,
        handler: Callable[[Dict[str, Any]], Any],
        prefetch_count: int = 10,
        durable: bool = True
    ) -> None:
        """Subscribe to messages.
        
        Args:
            queue_name: Queue name.
            routing_key: Message routing key.
            handler: Message handler function.
            prefetch_count: Number of messages to prefetch.
            durable: Whether queue should survive broker restart.
        """
        if not self._channel:
            await self.connect()
        
        # Declare queue
        queue = await self._channel.declare_queue(
            queue_name,
            durable=durable
        )
        
        # Bind queue to exchange
        await queue.bind(
            self._exchange,
            routing_key=routing_key
        )
        
        # Set QoS
        await self._channel.set_qos(prefetch_count=prefetch_count)
        
        # Store queue reference
        self._queues[queue_name] = queue
        
        # Start consuming messages
        async def _message_handler(message: AbstractIncomingMessage) -> None:
            async with message.process():
                try:
                    payload = json.loads(message.body.decode())
                    await handler(payload)
                except Exception as e:
                    # Log error and reject message
                    print(f"Error processing message: {e}")
                    await message.reject(requeue=True)
        
        await queue.consume(_message_handler)

    async def declare_dead_letter_queue(
        self,
        queue_name: str,
        routing_key: str,
        ttl: int = 1000 * 60 * 60  # 1 hour
    ) -> None:
        """Declare dead letter queue.
        
        Args:
            queue_name: Queue name.
            routing_key: Message routing key.
            ttl: Time to live in milliseconds.
        """
        if not self._channel:
            await self.connect()
        
        # Declare dead letter exchange
        dead_letter_exchange = await self._channel.declare_exchange(
            f"{queue_name}_dlx",
            aio_pika.ExchangeType.TOPIC
        )
        
        # Declare dead letter queue
        dead_letter_queue = await self._channel.declare_queue(
            f"{queue_name}_dlq",
            durable=True,
            arguments={
                "x-message-ttl": ttl,
                "x-dead-letter-exchange": self._exchange.name,
                "x-dead-letter-routing-key": routing_key
            }
        )
        
        # Bind dead letter queue
        await dead_letter_queue.bind(
            dead_letter_exchange,
            routing_key=routing_key
        )
