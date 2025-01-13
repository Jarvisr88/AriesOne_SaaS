"""Kafka event bus implementation."""
import json
from typing import Any, Callable, Dict, List, Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from pydantic import BaseModel

from core.messaging.events import Event, EventPublisher

class KafkaSettings(BaseModel):
    """Kafka connection settings."""
    
    BOOTSTRAP_SERVERS: List[str]
    CLIENT_ID: str
    GROUP_ID: str
    SECURITY_PROTOCOL: str = "PLAINTEXT"
    SASL_MECHANISM: Optional[str] = None
    SASL_USERNAME: Optional[str] = None
    SASL_PASSWORD: Optional[str] = None

class KafkaEventBus:
    """Kafka event bus implementation."""

    def __init__(self, settings: KafkaSettings):
        """Initialize Kafka event bus.
        
        Args:
            settings: Kafka connection settings.
        """
        self.settings = settings
        self._producer = self._create_producer()
        self._consumers: Dict[str, AIOKafkaConsumer] = {}
        self._handlers: Dict[str, List[Callable]] = {}

    def _create_producer(self) -> AIOKafkaProducer:
        """Create Kafka producer.
        
        Returns:
            Kafka producer.
        """
        return AIOKafkaProducer(
            bootstrap_servers=self.settings.BOOTSTRAP_SERVERS,
            client_id=self.settings.CLIENT_ID,
            security_protocol=self.settings.SECURITY_PROTOCOL,
            sasl_mechanism=self.settings.SASL_MECHANISM,
            sasl_plain_username=self.settings.SASL_USERNAME,
            sasl_plain_password=self.settings.SASL_PASSWORD,
            value_serializer=lambda v: json.dumps(v).encode()
        )

    async def start(self) -> None:
        """Start event bus."""
        await self._producer.start()
        for consumer in self._consumers.values():
            await consumer.start()

    async def stop(self) -> None:
        """Stop event bus."""
        await self._producer.stop()
        for consumer in self._consumers.values():
            await consumer.stop()

    async def publish(
        self,
        event: Event,
        publisher: EventPublisher
    ) -> None:
        """Publish event.
        
        Args:
            event: Event to publish.
            publisher: Event publisher metadata.
        """
        await self._producer.send_and_wait(
            topic=publisher.topic,
            value=event.dict(),
            key=publisher.partition_key.encode() if publisher.partition_key else None,
            headers=[
                (k.encode(), v.encode())
                for k, v in (publisher.headers or {}).items()
            ]
        )

    def subscribe(
        self,
        topic: str,
        handler: Callable[[Event], Any]
    ) -> None:
        """Subscribe to events.
        
        Args:
            topic: Topic to subscribe to.
            handler: Event handler function.
        """
        if topic not in self._handlers:
            self._handlers[topic] = []
            self._consumers[topic] = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self.settings.BOOTSTRAP_SERVERS,
                group_id=self.settings.GROUP_ID,
                security_protocol=self.settings.SECURITY_PROTOCOL,
                sasl_mechanism=self.settings.SASL_MECHANISM,
                sasl_plain_username=self.settings.SASL_USERNAME,
                sasl_plain_password=self.settings.SASL_PASSWORD,
                value_deserializer=lambda v: json.loads(v.decode())
            )
        
        self._handlers[topic].append(handler)

    async def process_events(self) -> None:
        """Process events from all subscribed topics."""
        for topic, consumer in self._consumers.items():
            async for msg in consumer:
                event_dict = msg.value
                event = Event.parse_obj(event_dict)
                
                for handler in self._handlers[topic]:
                    try:
                        await handler(event)
                    except Exception as e:
                        # Log error and continue processing
                        print(f"Error processing event: {e}")
                        continue
