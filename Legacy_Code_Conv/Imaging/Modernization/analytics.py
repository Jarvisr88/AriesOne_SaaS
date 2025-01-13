"""
Analytics service for image usage tracking.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from elasticsearch import AsyncElasticsearch
from prometheus_client import Counter, Histogram, Gauge
from .config import settings


# Metrics
UPLOAD_COUNTER = Counter(
    'image_uploads_total',
    'Total number of image uploads',
    ['company_id', 'status']
)

PROCESSING_TIME = Histogram(
    'image_processing_seconds',
    'Time spent processing images',
    ['operation']
)

STORAGE_USAGE = Gauge(
    'image_storage_bytes',
    'Total storage used by images',
    ['company_id']
)


class AnalyticsService:
    """Manages analytics and metrics."""
    
    def __init__(self):
        """Initialize analytics service."""
        self.logger = logging.getLogger(__name__)
        self.es = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
        
    async def track_upload(
        self,
        company_id: int,
        image_id: str,
        metadata: Dict[str, Any],
        status: str
    ) -> None:
        """Track image upload.
        
        Args:
            company_id: Company identifier
            image_id: Image identifier
            metadata: Image metadata
            status: Upload status
        """
        try:
            # Update metrics
            UPLOAD_COUNTER.labels(
                company_id=str(company_id),
                status=status
            ).inc()
            
            # Index event
            await self.es.index(
                index=f"image-events-{company_id}",
                document={
                    "event_type": "upload",
                    "company_id": company_id,
                    "image_id": image_id,
                    "metadata": metadata,
                    "status": status,
                    "timestamp": datetime.utcnow()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Upload tracking error: {str(e)}")
            
    async def track_processing(
        self,
        company_id: int,
        image_id: str,
        operation: str,
        duration: float,
        metadata: Dict[str, Any]
    ) -> None:
        """Track image processing.
        
        Args:
            company_id: Company identifier
            image_id: Image identifier
            operation: Processing operation
            duration: Duration in seconds
            metadata: Operation metadata
        """
        try:
            # Update metrics
            PROCESSING_TIME.labels(
                operation=operation
            ).observe(duration)
            
            # Index event
            await self.es.index(
                index=f"image-events-{company_id}",
                document={
                    "event_type": "processing",
                    "company_id": company_id,
                    "image_id": image_id,
                    "operation": operation,
                    "duration": duration,
                    "metadata": metadata,
                    "timestamp": datetime.utcnow()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Processing tracking error: {str(e)}")
            
    async def track_storage(
        self,
        company_id: int,
        total_bytes: int
    ) -> None:
        """Track storage usage.
        
        Args:
            company_id: Company identifier
            total_bytes: Total storage used
        """
        try:
            # Update metrics
            STORAGE_USAGE.labels(
                company_id=str(company_id)
            ).set(total_bytes)
            
            # Index event
            await self.es.index(
                index=f"image-events-{company_id}",
                document={
                    "event_type": "storage",
                    "company_id": company_id,
                    "total_bytes": total_bytes,
                    "timestamp": datetime.utcnow()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Storage tracking error: {str(e)}")
            
    async def get_usage_stats(
        self,
        company_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get usage statistics.
        
        Args:
            company_id: Company identifier
            days: Time period in days
            
        Returns:
            Usage statistics
        """
        try:
            # Calculate date range
            end = datetime.utcnow()
            start = end - timedelta(days=days)
            
            # Build query
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"company_id": company_id}},
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": start,
                                        "lte": end
                                    }
                                }
                            }
                        ]
                    }
                },
                "aggs": {
                    "uploads_per_day": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "day"
                        }
                    },
                    "upload_status": {
                        "terms": {
                            "field": "status.keyword"
                        }
                    },
                    "avg_processing_time": {
                        "avg": {
                            "field": "duration"
                        }
                    },
                    "storage_trend": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "day",
                            "aggs": {
                                "bytes": {
                                    "max": {
                                        "field": "total_bytes"
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            # Execute query
            result = await self.es.search(
                index=f"image-events-{company_id}",
                body=query,
                size=0
            )
            
            return self._format_stats(result)
            
        except Exception as e:
            self.logger.error(f"Stats error: {str(e)}")
            return {}
            
    def _format_stats(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format statistics results.
        
        Args:
            result: Elasticsearch response
            
        Returns:
            Formatted statistics
        """
        aggs = result.get("aggregations", {})
        
        return {
            "uploads": {
                "daily": [
                    {
                        "date": bucket["key_as_string"],
                        "count": bucket["doc_count"]
                    }
                    for bucket in aggs.get(
                        "uploads_per_day", {}
                    ).get("buckets", [])
                ],
                "by_status": [
                    {
                        "status": bucket["key"],
                        "count": bucket["doc_count"]
                    }
                    for bucket in aggs.get(
                        "upload_status", {}
                    ).get("buckets", [])
                ]
            },
            "processing": {
                "avg_time": aggs.get(
                    "avg_processing_time", {}
                ).get("value", 0)
            },
            "storage": {
                "trend": [
                    {
                        "date": bucket["key_as_string"],
                        "bytes": bucket["bytes"]["value"]
                    }
                    for bucket in aggs.get(
                        "storage_trend", {}
                    ).get("buckets", [])
                ]
            }
        }
