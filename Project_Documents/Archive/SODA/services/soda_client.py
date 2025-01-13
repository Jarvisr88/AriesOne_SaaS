"""SODA client service module."""

import asyncio
from typing import Optional, List, Dict, Any, TypeVar, Generic, Callable, AsyncIterator
from urllib.parse import urljoin, urlparse
import httpx
from pydantic import BaseModel, HttpUrl
from ..models.resource import ResourceMetadata, SodaResult
from ..utils.uri import SodaUri
from ..utils.exceptions import SodaError
from ..utils.validators import validate_resource_id

T = TypeVar('T', bound=BaseModel)

class SodaClient:
    """Client for interacting with SODA APIs."""
    
    def __init__(
        self,
        host: str,
        app_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30
    ):
        """Initialize SODA client."""
        if not host:
            raise ValueError("Host is required")
        
        # Ensure HTTPS
        parsed = urlparse(host)
        self.host = f"https://{parsed.netloc}"
        
        self.app_token = app_token
        self.username = username
        self.password = password
        self.timeout = timeout
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        headers = {}
        if self.app_token:
            headers['X-App-Token'] = self.app_token
        return headers
    
    async def get_metadata(self, resource_id: str) -> ResourceMetadata:
        """Get resource metadata."""
        validate_resource_id(resource_id)
        
        url = SodaUri.for_metadata(self.host, resource_id)
        async with self.client.stream('GET', url, headers=self._get_auth_headers()) as response:
            response.raise_for_status()
            data = await response.json()
            return ResourceMetadata(**data)
    
    async def get_metadata_page(
        self,
        page: int = 1,
        limit: int = 100
    ) -> List[ResourceMetadata]:
        """Get a page of resource metadata."""
        url = SodaUri.for_metadata_page(self.host, page, limit)
        async with self.client.stream('GET', url, headers=self._get_auth_headers()) as response:
            response.raise_for_status()
            data = await response.json()
            return [ResourceMetadata(**item) for item in data]
    
    async def query(
        self,
        resource_id: str,
        select: Optional[List[str]] = None,
        where: Optional[str] = None,
        order: Optional[str] = None,
        group: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query a SODA dataset."""
        validate_resource_id(resource_id)
        
        params = {}
        if select:
            params['$select'] = ','.join(select)
        if where:
            params['$where'] = where
        if order:
            params['$order'] = order
        if group:
            params['$group'] = group
        if limit:
            params['$limit'] = str(limit)
        if offset:
            params['$offset'] = str(offset)
        
        url = SodaUri.for_resource(self.host, resource_id)
        async with self.client.stream(
            'GET',
            url,
            params=params,
            headers=self._get_auth_headers()
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def upsert(
        self,
        resource_id: str,
        payload: List[Dict[str, Any]]
    ) -> SodaResult:
        """Upsert data to a SODA dataset."""
        validate_resource_id(resource_id)
        
        if not self.username or not self.password:
            raise ValueError("Write operations require authentication")
        
        url = SodaUri.for_resource(self.host, resource_id)
        async with self.client.stream(
            'POST',
            url,
            json=payload,
            headers=self._get_auth_headers(),
            auth=(self.username, self.password)
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return SodaResult(**data)
    
    async def batch_upsert(
        self,
        resource_id: str,
        payload: List[Dict[str, Any]],
        batch_size: int = 1000,
        break_function: Optional[Callable[[List[Dict[str, Any]], Dict[str, Any]], bool]] = None
    ) -> AsyncIterator[SodaResult]:
        """Batch upsert data to a SODA dataset."""
        validate_resource_id(resource_id)
        
        if not self.username or not self.password:
            raise ValueError("Write operations require authentication")
        
        batch = []
        for item in payload:
            batch.append(item)
            
            if break_function and break_function(batch, item):
                if batch:
                    yield await self.upsert(resource_id, batch)
                batch = []
                continue
            
            if len(batch) >= batch_size:
                yield await self.upsert(resource_id, batch)
                batch = []
        
        if batch:
            yield await self.upsert(resource_id, batch)
    
    async def delete_row(self, resource_id: str, row_id: str) -> SodaResult:
        """Delete a row from a SODA dataset."""
        validate_resource_id(resource_id)
        
        if not row_id:
            raise ValueError("Row ID is required")
        
        if not self.username or not self.password:
            raise ValueError("Write operations require authentication")
        
        url = SodaUri.for_resource_row(self.host, resource_id, row_id)
        async with self.client.stream(
            'DELETE',
            url,
            headers=self._get_auth_headers(),
            auth=(self.username, self.password)
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return SodaResult(**data)
