"""
CMN (Certificate of Medical Necessity) Repository Module

This module provides database access for CMN operations.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database.cmn_models import CmnRequestDB, CmnResponseDB, CmnResponseEntryDB
from ..models.cmn_models import CmnRequest, CmnResponse, CmnResponseEntry

class CmnRepository:
    """Repository for CMN data access."""

    async def save_response(
        self,
        response: CmnResponse,
        db: AsyncSession
    ) -> None:
        """
        Save a CMN response to the database.
        
        Args:
            response: The response to save
            db: Database session
        """
        # Convert to DB model
        response_db = CmnResponseDB(
            response_id=response.response_id,
            request_id=response.request_id,
            total_count=response.total_count,
            returned_count=response.returned_count,
            processing_time_ms=response.processing_time_ms
        )

        # Save entries
        entries_db = [
            CmnResponseEntryDB(
                entry_id=entry.entry_id,
                response_id=response.response_id,
                npi=entry.npi,
                hic=entry.hic,
                mbi=entry.mbi,
                hcpcs=entry.hcpcs,
                initial_date=entry.initial_date,
                recert_date=entry.recert_date,
                length_of_need=entry.length_of_need,
                status=entry.status
            )
            for entry in response.entries
        ]

        # Add to session
        db.add(response_db)
        db.add_all(entries_db)
        await db.commit()

    async def get_response(
        self,
        request_id: UUID,
        db: AsyncSession
    ) -> Optional[CmnResponse]:
        """
        Retrieve a CMN response by request ID.
        
        Args:
            request_id: UUID of the request
            db: Database session
        
        Returns:
            CmnResponse if found, None otherwise
        """
        # Query response
        stmt = select(CmnResponseDB).where(CmnResponseDB.request_id == request_id)
        result = await db.execute(stmt)
        response_db = result.scalar_one_or_none()

        if not response_db:
            return None

        # Query entries
        stmt = select(CmnResponseEntryDB).where(
            CmnResponseEntryDB.response_id == response_db.response_id
        )
        result = await db.execute(stmt)
        entries_db = result.scalars().all()

        # Convert to Pydantic models
        entries = [
            CmnResponseEntry(
                entry_id=entry.entry_id,
                npi=entry.npi,
                hic=entry.hic,
                mbi=entry.mbi,
                hcpcs=entry.hcpcs,
                initial_date=entry.initial_date,
                recert_date=entry.recert_date,
                length_of_need=entry.length_of_need,
                status=entry.status,
                last_updated=entry.last_updated
            )
            for entry in entries_db
        ]

        return CmnResponse(
            response_id=response_db.response_id,
            request_id=response_db.request_id,
            entries=entries,
            total_count=response_db.total_count,
            returned_count=response_db.returned_count,
            created_at=response_db.created_at,
            processing_time_ms=response_db.processing_time_ms
        )

    async def get_request_status(
        self,
        request_id: UUID,
        db: AsyncSession
    ) -> Optional[dict]:
        """
        Get the status of a CMN request.
        
        Args:
            request_id: UUID of the request
            db: Database session
        
        Returns:
            Dict containing status information if found
        """
        stmt = select(CmnResponseDB).where(CmnResponseDB.request_id == request_id)
        result = await db.execute(stmt)
        response_db = result.scalar_one_or_none()

        if not response_db:
            return None

        return {
            "request_id": request_id,
            "status": "completed",
            "created_at": response_db.created_at,
            "processing_time_ms": response_db.processing_time_ms,
            "total_results": response_db.total_count
        }
