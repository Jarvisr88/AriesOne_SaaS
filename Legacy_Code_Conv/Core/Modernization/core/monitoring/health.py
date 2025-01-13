"""
Core Health Check Module
Version: 1.0.0
Last Updated: 2025-01-10

This module provides health check functionality.
"""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..utils.config import get_settings
from ..utils.logging import CoreLogger

settings = get_settings()
logger = CoreLogger(__name__)


class HealthCheck:
    """Health check service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize health check service."""
        self._session = session
        self._status_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_duration = 60  # seconds
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            # Execute simple query
            result = await self._session.execute("SELECT 1")
            await result.scalar_one()
            
            return {
                "status": "healthy",
                "message": "Database connection is active",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_cache(self) -> Dict[str, Any]:
        """Check cache health."""
        try:
            # Implement Redis health check
            redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{redis_url}/ping") as response:
                    if response.status == 200:
                        return {
                            "status": "healthy",
                            "message": "Cache connection is active",
                            "timestamp": datetime.utcnow().isoformat()
                        }
            raise Exception("Cache connection failed")
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_event_bus(self) -> Dict[str, Any]:
        """Check event bus health."""
        try:
            # Implement RabbitMQ health check
            rabbitmq_url = f"http://{settings.EVENT_STORE_URL}:15672/api/health"
            async with aiohttp.ClientSession() as session:
                async with session.get(rabbitmq_url) as response:
                    if response.status == 200:
                        return {
                            "status": "healthy",
                            "message": "Event bus connection is active",
                            "timestamp": datetime.utcnow().isoformat()
                        }
            raise Exception("Event bus connection failed")
        except Exception as e:
            logger.error(f"Event bus health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_dependencies(self) -> Dict[str, Any]:
        """Check external dependencies."""
        dependencies = []
        
        # Add your external dependencies here
        # Example:
        # dependencies.append(("auth_service", "http://auth-service/health"))
        
        results = {}
        async with aiohttp.ClientSession() as session:
            for name, url in dependencies:
                try:
                    async with session.get(url) as response:
                        results[name] = {
                            "status": "healthy" if response.status == 200 else "unhealthy",
                            "message": await response.text(),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                except Exception as e:
                    results[name] = {
                        "status": "unhealthy",
                        "message": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        return results
    
    async def check_all(self, use_cache: bool = True) -> Dict[str, Any]:
        """Check health of all components."""
        # Return cached result if valid
        if use_cache and self._cache_time:
            cache_age = (datetime.utcnow() - self._cache_time).total_seconds()
            if cache_age < self._cache_duration:
                return self._status_cache
        
        # Run all health checks concurrently
        results = await asyncio.gather(
            self.check_database(),
            self.check_cache(),
            self.check_event_bus(),
            self.check_dependencies()
        )
        
        status = {
            "database": results[0],
            "cache": results[1],
            "event_bus": results[2],
            "dependencies": results[3],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update cache
        self._status_cache = status
        self._cache_time = datetime.utcnow()
        
        return status


async def get_health_check(
    session: AsyncSession = get_session()
) -> HealthCheck:
    """Get health check instance."""
    return HealthCheck(session)
