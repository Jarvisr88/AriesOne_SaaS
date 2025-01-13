"""
Maintenance service for system upkeep.
"""
from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime, timedelta
import aiofiles
import aiohttp
from .storage import StorageManager
from .cache import CacheManager
from .search import SearchService
from .config import settings


class MaintenanceService:
    """Manages system maintenance tasks."""
    
    def __init__(self):
        """Initialize maintenance service."""
        self.logger = logging.getLogger(__name__)
        self.storage = StorageManager()
        self.cache = CacheManager()
        self.search = SearchService()
        
    async def start_maintenance(self):
        """Start maintenance tasks."""
        try:
            # Start background tasks
            asyncio.create_task(
                self._cleanup_old_data()
            )
            asyncio.create_task(
                self._optimize_indexes()
            )
            asyncio.create_task(
                self._verify_backups()
            )
            asyncio.create_task(
                self._check_data_integrity()
            )
            
        except Exception as e:
            self.logger.error(f"Maintenance startup error: {str(e)}")
            
    async def _cleanup_old_data(
        self,
        interval: int = 86400  # Daily
    ):
        """Clean up old data.
        
        Args:
            interval: Cleanup interval in seconds
        """
        while True:
            try:
                # Get retention settings
                retention = await self._get_retention_settings()
                
                # Clean up old images
                await self._cleanup_old_images(
                    retention["images"]
                )
                
                # Clean up old logs
                await self._cleanup_old_logs(
                    retention["logs"]
                )
                
                # Clean up old metrics
                await self._cleanup_old_metrics(
                    retention["metrics"]
                )
                
                # Clean up cache
                await self._cleanup_cache()
                
            except Exception as e:
                self.logger.error(
                    f"Cleanup error: {str(e)}"
                )
                
            await asyncio.sleep(interval)
            
    async def _optimize_indexes(
        self,
        interval: int = 604800  # Weekly
    ):
        """Optimize search indexes.
        
        Args:
            interval: Optimization interval in seconds
        """
        while True:
            try:
                # Get company list
                companies = await self._get_active_companies()
                
                for company in companies:
                    # Optimize company index
                    await self._optimize_company_index(
                        company["id"]
                    )
                    
                    # Wait between companies
                    await asyncio.sleep(60)
                    
            except Exception as e:
                self.logger.error(
                    f"Index optimization error: {str(e)}"
                )
                
            await asyncio.sleep(interval)
            
    async def _verify_backups(
        self,
        interval: int = 86400  # Daily
    ):
        """Verify backup integrity.
        
        Args:
            interval: Verification interval in seconds
        """
        while True:
            try:
                # Get backup list
                backups = await self._get_backup_list()
                
                for backup in backups:
                    # Verify backup
                    await self._verify_backup(backup["id"])
                    
                    # Wait between backups
                    await asyncio.sleep(60)
                    
            except Exception as e:
                self.logger.error(
                    f"Backup verification error: {str(e)}"
                )
                
            await asyncio.sleep(interval)
            
    async def _check_data_integrity(
        self,
        interval: int = 86400  # Daily
    ):
        """Check data integrity.
        
        Args:
            interval: Check interval in seconds
        """
        while True:
            try:
                # Get company list
                companies = await self._get_active_companies()
                
                for company in companies:
                    # Check storage integrity
                    storage_issues = await self._check_storage_integrity(
                        company["id"]
                    )
                    
                    # Check index integrity
                    index_issues = await self._check_index_integrity(
                        company["id"]
                    )
                    
                    # Report issues
                    if storage_issues or index_issues:
                        await self._report_integrity_issues(
                            company["id"],
                            storage_issues,
                            index_issues
                        )
                        
                    # Wait between companies
                    await asyncio.sleep(60)
                    
            except Exception as e:
                self.logger.error(
                    f"Integrity check error: {str(e)}"
                )
                
            await asyncio.sleep(interval)
            
    async def _cleanup_old_images(
        self,
        retention_days: int
    ):
        """Clean up old images.
        
        Args:
            retention_days: Days to retain
        """
        try:
            cutoff = datetime.utcnow() - timedelta(
                days=retention_days
            )
            
            # Get companies
            companies = await self._get_active_companies()
            
            for company in companies:
                # List old images
                old_images = await self.storage.list_old_images(
                    company["id"],
                    cutoff
                )
                
                # Delete in batches
                for batch in self._chunk_list(old_images, 100):
                    tasks = []
                    for image in batch:
                        tasks.append(
                            self.storage.delete_image(
                                company["id"],
                                image["key"]
                            )
                        )
                    await asyncio.gather(*tasks)
                    
        except Exception as e:
            self.logger.error(f"Image cleanup error: {str(e)}")
            
    async def _cleanup_old_logs(
        self,
        retention_days: int
    ):
        """Clean up old logs.
        
        Args:
            retention_days: Days to retain
        """
        try:
            cutoff = datetime.utcnow() - timedelta(
                days=retention_days
            )
            
            # List old logs
            log_files = await self._list_old_logs(cutoff)
            
            # Delete old logs
            for file in log_files:
                try:
                    await aiofiles.os.remove(file)
                except Exception as e:
                    self.logger.error(
                        f"Log deletion error: {str(e)}"
                    )
                    
        except Exception as e:
            self.logger.error(f"Log cleanup error: {str(e)}")
            
    async def _cleanup_old_metrics(
        self,
        retention_days: int
    ):
        """Clean up old metrics.
        
        Args:
            retention_days: Days to retain
        """
        try:
            cutoff = datetime.utcnow() - timedelta(
                days=retention_days
            )
            
            # Delete old metrics
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{settings.PROMETHEUS_API}/admin/tsdb/delete_series",
                    params={
                        "match[]": "{job='imaging_service'}",
                        "end": cutoff.timestamp()
                    }
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Metric deletion failed: {await response.text()}"
                        )
                        
        except Exception as e:
            self.logger.error(f"Metric cleanup error: {str(e)}")
            
    async def _cleanup_cache(self):
        """Clean up expired cache entries."""
        try:
            # Get companies
            companies = await self._get_active_companies()
            
            for company in companies:
                # Invalidate old patterns
                await self.cache.invalidate_pattern(
                    f"{company['id']}:*"
                )
                
        except Exception as e:
            self.logger.error(f"Cache cleanup error: {str(e)}")
            
    async def _optimize_company_index(
        self,
        company_id: int
    ):
        """Optimize company search index.
        
        Args:
            company_id: Company identifier
        """
        try:
            # Force merge
            await self.search.optimize_index(company_id)
            
            # Refresh index
            await self.search.refresh_index(company_id)
            
        except Exception as e:
            self.logger.error(
                f"Index optimization error: {str(e)}"
            )
            
    async def _verify_backup(
        self,
        backup_id: str
    ):
        """Verify backup integrity.
        
        Args:
            backup_id: Backup identifier
        """
        try:
            # Get backup metadata
            metadata = await self._get_backup_metadata(
                backup_id
            )
            
            # Check files
            missing = await self._check_backup_files(
                backup_id,
                metadata["files"]
            )
            
            if missing:
                await self._report_backup_issues(
                    backup_id,
                    missing
                )
                
        except Exception as e:
            self.logger.error(
                f"Backup verification error: {str(e)}"
            )
            
    async def _check_storage_integrity(
        self,
        company_id: int
    ) -> List[Dict[str, Any]]:
        """Check storage integrity.
        
        Args:
            company_id: Company identifier
            
        Returns:
            List of issues found
        """
        issues = []
        
        try:
            # List all images
            images = await self.storage.list_images(
                company_id
            )
            
            for image in images:
                # Check image files
                if not await self._verify_image_files(
                    company_id,
                    image["key"]
                ):
                    issues.append({
                        "type": "missing_files",
                        "image_id": image["key"]
                    })
                    
        except Exception as e:
            self.logger.error(
                f"Storage integrity error: {str(e)}"
            )
            
        return issues
        
    async def _check_index_integrity(
        self,
        company_id: int
    ) -> List[Dict[str, Any]]:
        """Check index integrity.
        
        Args:
            company_id: Company identifier
            
        Returns:
            List of issues found
        """
        issues = []
        
        try:
            # Get indexed images
            indexed = await self.search.list_indexed_images(
                company_id
            )
            
            # Get stored images
            stored = await self.storage.list_images(
                company_id
            )
            
            # Find mismatches
            indexed_keys = {i["key"] for i in indexed}
            stored_keys = {s["key"] for s in stored}
            
            # Missing from index
            for key in stored_keys - indexed_keys:
                issues.append({
                    "type": "missing_from_index",
                    "image_id": key
                })
                
            # Missing from storage
            for key in indexed_keys - stored_keys:
                issues.append({
                    "type": "missing_from_storage",
                    "image_id": key
                })
                
        except Exception as e:
            self.logger.error(
                f"Index integrity error: {str(e)}"
            )
            
        return issues
        
    @staticmethod
    def _chunk_list(lst: list, n: int):
        """Split list into chunks.
        
        Args:
            lst: List to split
            n: Chunk size
            
        Yields:
            List chunks
        """
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
