"""
SODA (Socrata Open Data API) client implementation.
"""
from typing import Optional, List, Dict, Any, Union
import httpx
import asyncio
import json
from datetime import datetime
import logging
from .models import (
    SodaConfig, SodaResponse, SodaError, ResourceMetadata,
    SoqlQuery, SodaDataFormat
)
from .cache import cache_manager
from .monitoring import monitor

logger = logging.getLogger(__name__)

class SodaClient:
    """
    Async SODA client for interacting with Socrata Open Data APIs.
    """

    def __init__(self, config: SodaConfig):
        """Initialize SODA client."""
        self.config = config
        self.base_url = f"https://{config.domain}"
        self.headers = {
            "X-App-Token": config.app_token,
            "Accept": "application/json",
            "User-Agent": config.user_agent or "AriesOne-SODA-Client/1.0.0"
        }

        if config.username and config.password:
            auth = httpx.BasicAuth(config.username, config.password)
        else:
            auth = None

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            auth=auth,
            timeout=config.timeout,
            verify=config.verify_ssl,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the client session."""
        await self.client.aclose()

    @monitor()
    async def get_metadata(self, dataset_id: str) -> ResourceMetadata:
        """Get dataset metadata."""
        cache_key = f"metadata:{dataset_id}"
        
        if self.config.cache_enabled:
            cached = await cache_manager.get(cache_key)
            if cached:
                return ResourceMetadata(**cached)

        url = f"/api/views/{dataset_id}"
        response = await self._make_request("GET", url)
        metadata = ResourceMetadata(**response)

        if self.config.cache_enabled:
            await cache_manager.set(
                cache_key,
                metadata.dict(),
                expire=self.config.cache_ttl
            )

        return metadata

    @monitor()
    async def query(
        self,
        dataset_id: str,
        query: Optional[SoqlQuery] = None,
        format: SodaDataFormat = SodaDataFormat.JSON,
        use_cache: bool = True
    ) -> SodaResponse:
        """
        Query a dataset using SOQL.
        """
        start_time = datetime.now()
        query_str = query.to_query_string() if query else ""
        cache_key = f"query:{dataset_id}:{query_str}"

        if use_cache and self.config.cache_enabled:
            cached = await cache_manager.get(cache_key)
            if cached:
                return SodaResponse(**cached)

        url = f"/resource/{dataset_id}.{format}"
        if query_str:
            url = f"{url}?{query_str}"

        response = await self._make_request("GET", url)
        
        result = SodaResponse(
            data=response,
            metadata=await self.get_metadata(dataset_id),
            total_count=len(response),
            cached=False,
            request_time=(datetime.now() - start_time).total_seconds()
        )

        if use_cache and self.config.cache_enabled:
            await cache_manager.set(
                cache_key,
                result.dict(),
                expire=self.config.cache_ttl
            )

        return result

    @monitor()
    async def upsert(
        self,
        dataset_id: str,
        data: List[Dict[str, Any]]
    ) -> SodaResponse:
        """
        Create or update records in a dataset.
        """
        url = f"/resource/{dataset_id}"
        response = await self._make_request("POST", url, json=data)
        
        if self.config.cache_enabled:
            # Invalidate query cache for this dataset
            await cache_manager.delete_pattern(f"query:{dataset_id}:*")
        
        return SodaResponse(
            data=response,
            metadata=await self.get_metadata(dataset_id),
            total_count=len(response)
        )

    @monitor()
    async def delete(
        self,
        dataset_id: str,
        where: str
    ) -> SodaResponse:
        """
        Delete records from a dataset.
        """
        url = f"/resource/{dataset_id}"
        params = {"$where": where}
        response = await self._make_request("DELETE", url, params=params)
        
        if self.config.cache_enabled:
            # Invalidate query cache for this dataset
            await cache_manager.delete_pattern(f"query:{dataset_id}:*")
        
        return SodaResponse(
            data=response,
            metadata=await self.get_metadata(dataset_id),
            total_count=0
        )

    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Make an HTTP request to the SODA API.
        """
        retries = 0
        while retries < self.config.max_retries:
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_data = e.response.json()
                error = SodaError(
                    code=str(e.response.status_code),
                    message=error_data.get("message", str(e)),
                    details=error_data,
                    request_id=e.response.headers.get("X-Request-Id")
                )
                logger.error(f"SODA API error: {error.dict()}")
                raise ValueError(f"SODA API error: {error.message}")
            except httpx.RequestError as e:
                retries += 1
                if retries == self.config.max_retries:
                    logger.error(f"Max retries reached: {str(e)}")
                    raise
                await asyncio.sleep(2 ** retries)  # Exponential backoff
