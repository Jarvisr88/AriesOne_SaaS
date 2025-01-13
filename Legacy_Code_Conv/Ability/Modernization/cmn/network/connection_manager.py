"""
Connection Manager Module

Handles async network connections with connection pooling and circuit breaker pattern.
"""
from asyncio import Lock
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
import aiohttp
import asyncio
from fastapi import HTTPException, status
from pydantic import BaseModel

from ..config import get_settings
from ..utils.monitoring import get_logger

logger = get_logger(__name__)
settings = get_settings()

class ConnectionState(BaseModel):
    """Connection state tracking."""
    is_open: bool = True
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None

class CircuitBreaker:
    """Circuit breaker implementation."""
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        half_open_timeout: int = 30
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = timedelta(seconds=reset_timeout)
        self.half_open_timeout = timedelta(seconds=half_open_timeout)
        self.state = ConnectionState()
        self._lock = Lock()

    async def record_failure(self):
        """Record a connection failure."""
        async with self._lock:
            self.state.failure_count += 1
            self.state.last_failure = datetime.utcnow()
            
            if (self.state.failure_count >= self.failure_threshold and 
                self.state.is_open):
                self.state.is_open = False
                logger.warning(f"Circuit breaker opened after {self.failure_threshold} failures")

    async def record_success(self):
        """Record a successful connection."""
        async with self._lock:
            self.state.failure_count = 0
            self.state.last_success = datetime.utcnow()
            self.state.is_open = True

    async def can_execute(self) -> bool:
        """Check if operation can be executed."""
        async with self._lock:
            if self.state.is_open:
                return True

            now = datetime.utcnow()
            if (self.state.last_failure and 
                now - self.state.last_failure >= self.reset_timeout):
                self.state.is_open = True
                self.state.failure_count = 0
                return True

            if (self.state.last_failure and 
                now - self.state.last_failure >= self.half_open_timeout):
                return True

            return False

class ConnectionPool:
    """Async connection pool with circuit breaker."""
    def __init__(
        self,
        pool_size: int = 10,
        timeout: float = 30.0,
        retry_attempts: int = 3
    ):
        self.pool_size = pool_size
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session: Optional[aiohttp.ClientSession] = None
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._active_connections: Set[str] = set()
        self._pool_lock = Lock()

    async def initialize(self):
        """Initialize connection pool."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close all connections."""
        if self.session:
            await self.session.close()
            self.session = None

    def _get_circuit_breaker(self, endpoint: str) -> CircuitBreaker:
        """Get or create circuit breaker for endpoint."""
        if endpoint not in self._circuit_breakers:
            self._circuit_breakers[endpoint] = CircuitBreaker()
        return self._circuit_breakers[endpoint]

    @asynccontextmanager
    async def get_connection(self, endpoint: str):
        """Get connection from pool with circuit breaker protection."""
        if not self.session:
            await self.initialize()

        circuit_breaker = self._get_circuit_breaker(endpoint)
        
        if not await circuit_breaker.can_execute():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable"
            )

        async with self._pool_lock:
            if len(self._active_connections) >= self.pool_size:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Connection pool exhausted"
                )
            self._active_connections.add(endpoint)

        try:
            for attempt in range(self.retry_attempts):
                try:
                    async with self.session.get(endpoint) as response:
                        if response.status < 500:
                            await circuit_breaker.record_success()
                            yield response
                            return
                        raise HTTPException(
                            status_code=response.status,
                            detail=await response.text()
                        )
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt == self.retry_attempts - 1:
                        await circuit_breaker.record_failure()
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=str(e)
                        )
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        finally:
            async with self._pool_lock:
                self._active_connections.remove(endpoint)

connection_pool = ConnectionPool(
    pool_size=settings.POOL_SIZE,
    timeout=settings.CONNECTION_TIMEOUT,
    retry_attempts=settings.RETRY_ATTEMPTS
)
