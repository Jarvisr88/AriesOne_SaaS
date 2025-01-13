from typing import Dict, List, Optional, Type
import asyncio
from datetime import datetime
from app.services.cdn.base import (
    BaseCDN,
    CDNProvider,
    CDNRegion,
    OptimizationType,
    CDNException
)
from app.services.cdn.cloudfront import CloudFrontCDN
from app.core.config import settings
from app.core.logging import logger
from app.core.monitoring import metrics

class CDNManager:
    def __init__(self):
        self.cdns: Dict[str, BaseCDN] = {}
        self.provider_map: Dict[CDNProvider, Type[BaseCDN]] = {
            CDNProvider.CLOUDFRONT: CloudFrontCDN,
            # Add other CDN providers here
        }
        self._setup_cdns()
        self._start_health_monitoring()

    def _setup_cdns(self) -> None:
        """Setup CDN providers"""
        for provider_config in settings.CDN_CONFIGS:
            provider = CDNProvider(provider_config["provider"])
            region = CDNRegion(provider_config["region"])
            
            cdn_class = self.provider_map.get(provider)
            if cdn_class:
                cdn = cdn_class(region, provider_config)
                key = f"{provider}:{region}"
                self.cdns[key] = cdn
                logger.info(f"Initialized CDN: {key}")

    def _start_health_monitoring(self) -> None:
        """Start health monitoring for all CDNs"""
        for cdn in self.cdns.values():
            asyncio.create_task(cdn.monitor_health())

    def _get_best_cdn(
        self,
        provider: Optional[CDNProvider] = None,
        region: Optional[CDNRegion] = None
    ) -> BaseCDN:
        """Get best available CDN based on health and latency"""
        available_cdns = []
        
        for key, cdn in self.cdns.items():
            if not cdn.is_healthy():
                continue
                
            if provider and cdn.provider != provider:
                continue
                
            if region and cdn.region != region:
                continue
                
            available_cdns.append(cdn)
        
        if not available_cdns:
            raise CDNException("No healthy CDN available")
        
        # Sort by latency
        return min(available_cdns, key=lambda x: x.get_latency())

    async def upload_file(
        self,
        file_path: str,
        content: bytes,
        content_type: str,
        provider: Optional[CDNProvider] = None,
        region: Optional[CDNRegion] = None
    ) -> Dict[str, str]:
        """Upload file to multiple CDNs"""
        urls = {}
        errors = []
        
        # Try primary CDN first
        try:
            primary_cdn = self._get_best_cdn(provider, region)
            url = await primary_cdn.upload_file(
                file_path,
                content,
                content_type
            )
            urls[f"{primary_cdn.provider}:{primary_cdn.region}"] = url
        except Exception as e:
            errors.append(str(e))
            metrics.cdn_upload_errors.inc()
        
        # Upload to other CDNs asynchronously
        if not provider and not region:
            tasks = []
            for key, cdn in self.cdns.items():
                if cdn != primary_cdn and cdn.is_healthy():
                    tasks.append(
                        cdn.upload_file(file_path, content, content_type)
                    )
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for cdn, result in zip(self.cdns.values(), results):
                    if isinstance(result, Exception):
                        errors.append(str(result))
                        metrics.cdn_upload_errors.inc()
                    else:
                        urls[f"{cdn.provider}:{cdn.region}"] = result
        
        if not urls:
            raise CDNException(
                f"Failed to upload to any CDN: {', '.join(errors)}"
            )
        
        return urls

    async def get_url(
        self,
        file_path: str,
        ttl: Optional[int] = None,
        provider: Optional[CDNProvider] = None,
        region: Optional[CDNRegion] = None
    ) -> str:
        """Get URL from best available CDN"""
        cdn = self._get_best_cdn(provider, region)
        try:
            return await cdn.get_url(file_path, ttl)
        except Exception as e:
            metrics.cdn_url_errors.inc()
            raise CDNException(f"Failed to get URL: {e}")

    async def invalidate(
        self,
        paths: List[str],
        provider: Optional[CDNProvider] = None,
        region: Optional[CDNRegion] = None
    ) -> None:
        """Invalidate cache in all CDNs"""
        errors = []
        
        for cdn in self.cdns.values():
            if not cdn.is_healthy():
                continue
                
            if provider and cdn.provider != provider:
                continue
                
            if region and cdn.region != region:
                continue
                
            try:
                await cdn.invalidate(paths)
            except Exception as e:
                errors.append(str(e))
                metrics.cdn_invalidation_errors.inc()
        
        if errors:
            raise CDNException(
                f"Failed to invalidate in some CDNs: {', '.join(errors)}"
            )

    async def optimize(
        self,
        file_path: str,
        optimization_type: OptimizationType,
        provider: Optional[CDNProvider] = None,
        region: Optional[CDNRegion] = None
    ) -> str:
        """Optimize file using best available CDN"""
        cdn = self._get_best_cdn(provider, region)
        try:
            return await cdn.optimize(file_path, optimization_type)
        except Exception as e:
            metrics.cdn_optimization_errors.inc()
            raise CDNException(f"Failed to optimize file: {e}")

    def get_health_status(self) -> Dict[str, Dict]:
        """Get health status of all CDNs"""
        return {
            key: {
                "healthy": cdn.is_healthy(),
                "latency": cdn.get_latency(),
                "last_check": cdn.status.last_check.isoformat(),
                "error_count": cdn.status.error_count
            }
            for key, cdn in self.cdns.items()
        }

# Create global CDN manager
cdn_manager = CDNManager()
