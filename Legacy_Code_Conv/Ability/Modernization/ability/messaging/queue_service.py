"""
Message Queue Service Module

This module handles message queue operations using RabbitMQ.
"""
from datetime import datetime
import json
from typing import Any, Dict, Optional, Callable
import uuid

import aio_pika
from fastapi import BackgroundTasks
from pydantic import BaseModel

from ..config import Settings
from ..monitoring.telemetry import TelemetryService


class QueueMessage(BaseModel):
    """Base message model for queue operations."""
    message_id: str = str(uuid.uuid4())
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    retry_count: int = 0


class QueueService:
    """Service for handling RabbitMQ operations."""

    def __init__(
        self,
        settings: Settings,
        telemetry: TelemetryService,
        background_tasks: BackgroundTasks
    ):
        """Initialize queue service."""
        self.settings = settings
        self.telemetry = telemetry
        self.background_tasks = background_tasks
        self.connection = None
        self.channel = None
        self._handlers = {}

    async def connect(self):
        """Establish connection to RabbitMQ."""
        if not self.connection:
            self.connection = await aio_pika.connect_robust(
                self.settings.rabbitmq_url,
                client_properties={
                    "connection_name": "ability_service"
                }
            )
            self.channel = await self.connection.channel()
            await self._setup_exchanges()
            await self._setup_queues()

    async def _setup_exchanges(self):
        """Set up RabbitMQ exchanges."""
        # Main exchange for eligibility events
        self.eligibility_exchange = await self.channel.declare_exchange(
            "eligibility",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        # Dead letter exchange
        self.dlx_exchange = await self.channel.declare_exchange(
            "eligibility.dlx",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

    async def _setup_queues(self):
        """Set up RabbitMQ queues."""
        # Main queues
        self.request_queue = await self.channel.declare_queue(
            "eligibility.requests",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "eligibility.dlx",
                "x-dead-letter-routing-key": "eligibility.failed"
            }
        )
        
        self.response_queue = await self.channel.declare_queue(
            "eligibility.responses",
            durable=True
        )
        
        # Dead letter queue
        self.dlq = await self.channel.declare_queue(
            "eligibility.dlq",
            durable=True
        )
        
        await self.dlq.bind(self.dlx_exchange, "eligibility.failed")

    async def publish(
        self,
        message: QueueMessage,
        routing_key: str,
        priority: int = 0
    ):
        """Publish message to queue."""
        try:
            await self.connect()
            
            message_body = message.json().encode()
            
            await self.eligibility_exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    message_id=message.message_id,
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    priority=priority,
                    headers={
                        "retry_count": message.retry_count
                    }
                ),
                routing_key=routing_key
            )
            
            await self.telemetry.log_info(
                "message_published",
                {"message_id": message.message_id, "routing_key": routing_key}
            )
            
        except Exception as e:
            await self.telemetry.log_error(
                "publish_error",
                str(e),
                {"message_id": message.message_id, "routing_key": routing_key}
            )
            raise

    async def subscribe(
        self,
        queue_name: str,
        callback: Callable,
        prefetch_count: int = 10
    ):
        """Subscribe to queue messages."""
        try:
            await self.connect()
            await self.channel.set_qos(prefetch_count=prefetch_count)
            
            queue = await self.channel.declare_queue(queue_name, durable=True)
            
            async def _message_handler(message: aio_pika.IncomingMessage):
                async with message.process():
                    try:
                        payload = json.loads(message.body.decode())
                        queue_message = QueueMessage(**payload)
                        
                        # Execute callback in background task
                        self.background_tasks.add_task(
                            callback,
                            queue_message
                        )
                        
                    except Exception as e:
                        retry_count = message.headers.get("retry_count", 0)
                        if retry_count < self.settings.max_retry_count:
                            # Retry with incremented count
                            await self.publish(
                                QueueMessage(
                                    **payload,
                                    retry_count=retry_count + 1
                                ),
                                message.routing_key
                            )
                        else:
                            # Send to dead letter queue
                            await self.dlx_exchange.publish(
                                message,
                                routing_key="eligibility.failed"
                            )
                        
                        await self.telemetry.log_error(
                            "message_processing_error",
                            str(e),
                            {"message_id": message.message_id}
                        )
            
            await queue.consume(_message_handler)
            
            await self.telemetry.log_info(
                "subscription_started",
                {"queue": queue_name}
            )
            
        except Exception as e:
            await self.telemetry.log_error(
                "subscribe_error",
                str(e),
                {"queue": queue_name}
            )
            raise

    async def close(self):
        """Close queue connections."""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
