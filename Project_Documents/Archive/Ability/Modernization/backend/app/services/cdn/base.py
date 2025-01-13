from typing import Optional, Dict, List
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from app.core.config import settings
from app.core.logging import logger
from app.core.monitoring import metrics

class CDNProvider(str, Enum):
    CLOUDFRONT = "cloudfront"
    CLOUDFLARE = "cloudflare"
    FASTLY = "fastly"

class CDNRegion(str, Enum):
    US_EAST = "us-east"
    US_WEST = "us-west"
    EU_WEST = "eu-west"
    ASIA_EAST = "asia-east"

class OptimizationType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    JS = "javascript"
    CSS = "css"
    HTML = "html"

class CDNStatus:
    def __init__(self):
        self.last_check: datetime = datetime.utcnow()
        self.is_healthy: bool = True
        self.latency: float = 0.0
        self.error_count: int = 0
        self.error_threshold: int = 3
        self.check_interval: int = 60  # seconds

    def mark_healthy(self, latency: float) -> None:
        self.is_healthy = True
        self.latency = latency
        self.error_count = 0
        self.last_check = datetime.utcnow()

    def mark_unhealthy(self) -> None:
        self.error_count += 1
        if self.error_count >= self.error_threshold:
            self.is_healthy = False
        self.last_check = datetime.utcnow()

    def needs_check(self) -> bool:
        return (datetime.utcnow() - self.last_check).seconds >= self.check_interval

class BaseCDN(ABC):
    def __init__(
        self,
        provider: CDNProvider,
        region: CDNRegion,
        config: Dict
    ):
        self.provider = provider
        self.region = region
        self.config = config
        self.status = CDNStatus()
        self._setup_monitoring()

    def _setup_monitoring(self) -> None:
        """Setup monitoring metrics"""
        self.metrics = {
            "requests": metrics.cdn_requests.labels(
                provider=self.provider,
                region=self.region
            ),
            "errors": metrics.cdn_errors.labels(
                provider=self.provider,
                region=self.region
            ),
            "latency": metrics.cdn_latency.labels(
                provider=self.provider,
                region=self.region
            ),
            "cache_hits": metrics.cdn_cache_hits.labels(
                provider=self.provider,
                region=self.region
            ),
            "cache_misses": metrics.cdn_cache_misses.labels(
                provider=self.provider,
                region=self.region
            ),
            "bandwidth": metrics.cdn_bandwidth.labels(
                provider=self.provider,
                region=self.region
            )
        }

    @abstractmethod
    async def health_check(self) -> bool:
        """Check CDN health"""
        pass

    @abstractmethod
    async def upload_file(
        self,
        file_path: str,
        content: bytes,
        content_type: str
    ) -> str:
        """Upload file to CDN"""
        pass

    @abstractmethod
    async def get_url(
        self,
        file_path: str,
        ttl: Optional[int] = None
    ) -> str:
        """Get CDN URL for file"""
        pass

    @abstractmethod
    async def invalidate(self, paths: List[str]) -> None:
        """Invalidate CDN cache for paths"""
        pass

    @abstractmethod
    async def optimize(
        self,
        file_path: str,
        optimization_type: OptimizationType
    ) -> str:
        """Optimize file using CDN features"""
        pass

    async def monitor_health(self) -> None:
        """Monitor CDN health continuously"""
        while True:
            try:
                if self.status.needs_check():
                    start_time = datetime.utcnow()
                    is_healthy = await self.health_check()
                    latency = (datetime.utcnow() - start_time).total_seconds()

                    if is_healthy:
                        self.status.mark_healthy(latency)
                        self.metrics["latency"].observe(latency)
                    else:
                        self.status.mark_unhealthy()
                        self.metrics["errors"].inc()

            except Exception as e:
                logger.error(f"Health check error for {self.provider}: {e}")
                self.status.mark_unhealthy()
                self.metrics["errors"].inc()

            await asyncio.sleep(10)

    def track_request(self, size: int, cache_hit: bool) -> None:
        """Track CDN request metrics"""
        self.metrics["requests"].inc()
        self.metrics["bandwidth"].inc(size)
        
        if cache_hit:
            self.metrics["cache_hits"].inc()
        else:
            self.metrics["cache_misses"].inc()

    def is_healthy(self) -> bool:
        """Check if CDN is healthy"""
        return self.status.is_healthy

    def get_latency(self) -> float:
        """Get CDN latency"""
        return self.status.latency

class CDNException(Exception):
    """Base exception for CDN operations"""
    pass

class CDNUploadError(CDNException):
    """Error during file upload"""
    pass

class CDNInvalidationError(CDNException):
    """Error during cache invalidation"""
    pass

class CDNOptimizationError(CDNException):
    """Error during file optimization"""
    pass
