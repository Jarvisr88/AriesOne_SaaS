"""
CMN (Certificate of Medical Necessity) API Endpoints

This module provides FastAPI endpoints for CMN operations.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.cmn_models import CmnRequest, CmnResponse, CmnSearchCriteria
from ..services.cmn_service import CmnService
from ..dependencies import get_db, get_current_user, get_cmn_service

router = APIRouter(prefix="/api/v1/cmn", tags=["cmn"])

@router.post("/search", response_model=CmnResponse)
async def search_cmn(
    request: CmnRequest,
    current_user = Depends(get_current_user),
    cmn_service: CmnService = Depends(get_cmn_service),
    db: AsyncSession = Depends(get_db)
) -> CmnResponse:
    """
    Search for CMN records based on provided criteria.
    
    Args:
        request: CMN search request
        current_user: Authenticated user
        cmn_service: CMN service instance
        db: Database session
    
    Returns:
        CmnResponse containing matching records
    
    Raises:
        HTTPException: If request is invalid or processing fails
    """
    try:
        return await cmn_service.process_request(request, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{request_id}", response_model=CmnResponse)
async def get_cmn_response(
    request_id: UUID,
    current_user = Depends(get_current_user),
    cmn_service: CmnService = Depends(get_cmn_service),
    db: AsyncSession = Depends(get_db)
) -> CmnResponse:
    """
    Retrieve a specific CMN response by request ID.
    
    Args:
        request_id: UUID of the request
        current_user: Authenticated user
        cmn_service: CMN service instance
        db: Database session
    
    Returns:
        CmnResponse for the specified request
    
    Raises:
        HTTPException: If request not found or access denied
    """
    try:
        response = await cmn_service.get_response(request_id, db)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{request_id}")
async def get_request_status(
    request_id: UUID,
    current_user = Depends(get_current_user),
    cmn_service: CmnService = Depends(get_cmn_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the processing status of a CMN request.
    
    Args:
        request_id: UUID of the request
        current_user: Authenticated user
        cmn_service: CMN service instance
        db: Database session
    
    Returns:
        Dict containing status information
    
    Raises:
        HTTPException: If request not found
    """
    try:
        status = await cmn_service.get_request_status(request_id, db)
        if not status:
            raise HTTPException(status_code=404, detail="Request not found")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
