"""SODA URI utilities module."""

from typing import Optional
from urllib.parse import urljoin, quote

class SodaUri:
    """Utility class for building SODA URIs."""
    
    @staticmethod
    def for_metadata(host: str, resource_id: str) -> str:
        """Build URI for resource metadata."""
        return urljoin(host, f"/api/views/{quote(resource_id)}")
    
    @staticmethod
    def for_metadata_page(
        host: str,
        page: int = 1,
        limit: int = 100
    ) -> str:
        """Build URI for metadata page."""
        offset = (page - 1) * limit
        return urljoin(
            host,
            f"/api/views?limit={limit}&offset={offset}"
        )
    
    @staticmethod
    def for_resource(host: str, resource_id: str) -> str:
        """Build URI for resource data."""
        return urljoin(
            host,
            f"/resource/{quote(resource_id)}.json"
        )
    
    @staticmethod
    def for_resource_row(
        host: str,
        resource_id: str,
        row_id: str
    ) -> str:
        """Build URI for specific resource row."""
        return urljoin(
            host,
            f"/resource/{quote(resource_id)}/{quote(row_id)}"
        )
