"""
CMN (Certificate of Medical Necessity) Service Module

This module provides the business logic for CMN operations.
"""
import time
from typing import Dict, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.cmn_models import CmnRequest, CmnResponse, CmnResponseEntry
from ..repositories.cmn_repository import CmnRepository
from ..utils.medicare_client import MedicareClient
from ..utils.validation import validate_request

class CmnService:
    """Service for handling CMN operations."""

    def __init__(
        self,
        repository: CmnRepository,
        medicare_client: MedicareClient,
        cache_service = None
    ):
        """
        Initialize CMN service.
        
        Args:
            repository: CMN repository for data access
            medicare_client: Client for Medicare mainframe interaction
            cache_service: Optional cache service
        """
        self.repository = repository
        self.medicare_client = medicare_client
        self.cache_service = cache_service

    async def process_request(
        self,
        request: CmnRequest,
        db: AsyncSession
    ) -> CmnResponse:
        """
        Process a CMN search request.
        
        Args:
            request: The search request
            db: Database session
        
        Returns:
            CmnResponse containing search results
        
        Raises:
            ValueError: If request validation fails
            HTTPException: If processing fails
        """
        # Validate request
        validate_request(request)
        
        start_time = time.time()
        
        try:
            # Check cache if available
            if self.cache_service:
                cached_response = await self.cache_service.get(str(request.request_id))
                if cached_response:
                    return cached_response

            # Process request
            if request.mock_response:
                entries = await self._get_mock_entries(request)
            else:
                entries = await self.medicare_client.search_cmn(
                    request.medicare_mainframe,
                    request.search_criteria
                )

            # Create response
            response = CmnResponse(
                request_id=request.request_id,
                entries=entries,
                total_count=len(entries),
                returned_count=len(entries),
                processing_time_ms=(time.time() - start_time) * 1000
            )

            # Save to database
            await self.repository.save_response(response, db)

            # Cache if available
            if self.cache_service:
                await self.cache_service.set(
                    str(request.request_id),
                    response,
                    expire=3600
                )

            return response

        except Exception as e:
            # Log error
            raise HTTPException(
                status_code=500,
                detail=f"Error processing request: {str(e)}"
            )

    async def get_response(
        self,
        request_id: UUID,
        db: AsyncSession
    ) -> Optional[CmnResponse]:
        """
        Retrieve a specific CMN response.
        
        Args:
            request_id: UUID of the request
            db: Database session
        
        Returns:
            CmnResponse if found, None otherwise
        """
        return await self.repository.get_response(request_id, db)

    async def get_request_status(
        self,
        request_id: UUID,
        db: AsyncSession
    ) -> Optional[Dict]:
        """
        Get the status of a CMN request.
        
        Args:
            request_id: UUID of the request
            db: Database session
        
        Returns:
            Dict containing status information if found
        """
        return await self.repository.get_request_status(request_id, db)

    async def _get_mock_entries(self, request: CmnRequest) -> list[CmnResponseEntry]:
        """Generate mock entries for testing."""
        # Implementation for mock data generation
        return []
