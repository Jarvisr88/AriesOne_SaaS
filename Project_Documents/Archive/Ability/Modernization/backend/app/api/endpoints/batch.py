from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from datetime import datetime

from app.models.batch import (
    BatchJob,
    BatchProgress,
    BatchResult,
    BatchType,
    BatchStatus,
)
from app.services.batch_processor import batch_processor
from app.core.dependencies import get_current_user, RateLimiter
from app.core.logging import logger

router = APIRouter()
rate_limiter = RateLimiter(requests_per_minute=30)

@router.post(
    "/batch",
    response_model=str,
    summary="Submit batch job",
    response_description="Returns batch job ID",
)
async def submit_batch(
    batch_job: BatchJob,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Submit a new batch job for processing.
    
    Parameters:
    - batch_job: Batch job configuration and items
    
    Returns:
    - Batch job ID for tracking
    """
    try:
        batch_id = await batch_processor.submit_batch(batch_job)
        await batch_processor.process_batch(batch_id, background_tasks)
        return batch_id
    except Exception as e:
        logger.error(f"Error submitting batch job: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit batch job: {str(e)}",
        )

@router.get(
    "/batch/{batch_id}/progress",
    response_model=BatchProgress,
    summary="Get batch progress",
    response_description="Returns current batch processing progress",
)
async def get_batch_progress(
    batch_id: str,
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Get current progress of a batch job.
    
    Parameters:
    - batch_id: Batch job identifier
    
    Returns:
    - Current processing progress and statistics
    """
    progress = await batch_processor.get_batch_progress(batch_id)
    if not progress:
        raise HTTPException(
            status_code=404,
            detail="Batch job not found",
        )
    return progress

@router.get(
    "/batch/{batch_id}/result",
    response_model=BatchResult,
    summary="Get batch result",
    response_description="Returns final batch processing result",
)
async def get_batch_result(
    batch_id: str,
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Get final results of a completed batch job.
    
    Parameters:
    - batch_id: Batch job identifier
    
    Returns:
    - Final processing results and statistics
    """
    result = await batch_processor.get_batch_result(batch_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Batch results not found",
        )
    return result

@router.post(
    "/batch/claims",
    response_model=str,
    summary="Submit claims batch",
    response_description="Returns batch job ID",
)
async def submit_claims_batch(
    claims: List[dict],
    background_tasks: BackgroundTasks,
    priority: int = Query(2, ge=1, le=3, description="Batch priority (1=Low, 2=Medium, 3=High)"),
    max_retries: int = Query(3, ge=1, le=5, description="Maximum retry attempts"),
    concurrent_limit: int = Query(10, ge=1, le=50, description="Maximum concurrent operations"),
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Submit a batch of claims for processing.
    
    Parameters:
    - claims: List of claim data
    - priority: Processing priority
    - max_retries: Maximum retry attempts
    - concurrent_limit: Maximum concurrent operations
    
    Returns:
    - Batch job ID for tracking
    """
    try:
        batch_items = [
            {
                "item_id": f"claim_{i}",
                "data": claim,
            }
            for i, claim in enumerate(claims)
        ]

        batch_job = BatchJob(
            type=BatchType.CLAIM_SUBMISSION,
            priority=priority,
            items=batch_items,
            creator_id=current_user.id,
            max_retries=max_retries,
            concurrent_limit=concurrent_limit,
        )

        batch_id = await batch_processor.submit_batch(batch_job)
        await batch_processor.process_batch(batch_id, background_tasks)
        return batch_id
    except Exception as e:
        logger.error(f"Error submitting claims batch: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit claims batch: {str(e)}",
        )

@router.post(
    "/batch/eligibility",
    response_model=str,
    summary="Submit eligibility checks batch",
    response_description="Returns batch job ID",
)
async def submit_eligibility_batch(
    checks: List[dict],
    background_tasks: BackgroundTasks,
    priority: int = Query(2, ge=1, le=3, description="Batch priority (1=Low, 2=Medium, 3=High)"),
    max_retries: int = Query(3, ge=1, le=5, description="Maximum retry attempts"),
    concurrent_limit: int = Query(10, ge=1, le=50, description="Maximum concurrent operations"),
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Submit a batch of eligibility checks.
    
    Parameters:
    - checks: List of eligibility check data
    - priority: Processing priority
    - max_retries: Maximum retry attempts
    - concurrent_limit: Maximum concurrent operations
    
    Returns:
    - Batch job ID for tracking
    """
    try:
        batch_items = [
            {
                "item_id": f"eligibility_{i}",
                "data": check,
            }
            for i, check in enumerate(checks)
        ]

        batch_job = BatchJob(
            type=BatchType.ELIGIBILITY_CHECK,
            priority=priority,
            items=batch_items,
            creator_id=current_user.id,
            max_retries=max_retries,
            concurrent_limit=concurrent_limit,
        )

        batch_id = await batch_processor.submit_batch(batch_job)
        await batch_processor.process_batch(batch_id, background_tasks)
        return batch_id
    except Exception as e:
        logger.error(f"Error submitting eligibility batch: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit eligibility batch: {str(e)}",
        )
