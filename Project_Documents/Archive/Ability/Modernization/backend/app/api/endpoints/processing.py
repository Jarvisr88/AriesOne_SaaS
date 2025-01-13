from typing import Dict, Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from app.services.processing.service import processing_service
from app.core.logging import logger
from app.core.monitoring import metrics

router = APIRouter()

class ProcessingOptions(BaseModel):
    """Processing options"""
    size: Optional[tuple[int, int]]
    format: Optional[str]
    filters: Optional[List[str]]

class ProcessingResponse(BaseModel):
    """Processing response"""
    job_id: str
    status: str
    input_url: str
    output_urls: Optional[Dict[str, str]]
    quality: Optional[Dict]
    error: Optional[str]

@router.post(
    "/process",
    response_model=ProcessingResponse,
    summary="Process file synchronously",
    description="Process a file synchronously with quality analysis and OCR"
)
async def process_sync(
    file: UploadFile = File(...),
    options: Optional[ProcessingOptions] = None
):
    """
    Process file synchronously with:
    1. Quality analysis
    2. OCR processing
    3. Image processing
    4. Result upload
    """
    try:
        content = await file.read()
        result = await processing_service.process_sync(
            content,
            file.content_type,
            options.dict() if options else None
        )
        return ProcessingResponse(**result.to_dict())
    except Exception as e:
        logger.error(f"Processing error: {e}")
        metrics.processing_error_rate.inc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post(
    "/process/async",
    response_model=ProcessingResponse,
    summary="Process file asynchronously",
    description="Queue file for asynchronous processing"
)
async def process_async(
    file: UploadFile = File(...),
    options: Optional[ProcessingOptions] = None
):
    """
    Queue file for processing with:
    1. File upload
    2. Job creation
    3. Queue management
    4. Status tracking
    """
    try:
        content = await file.read()
        job_id = await processing_service.process_async(
            content,
            file.content_type,
            options.dict() if options else None
        )
        status = await processing_service.get_status(job_id)
        return ProcessingResponse(**status)
    except Exception as e:
        logger.error(f"Job queueing error: {e}")
        metrics.processing_error_rate.inc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get(
    "/process/{job_id}",
    response_model=ProcessingResponse,
    summary="Get processing status",
    description="Get status of processing job"
)
async def get_status(job_id: str):
    """
    Get processing status with:
    1. Job lookup
    2. Status check
    3. Result retrieval
    4. Error handling
    """
    try:
        status = await processing_service.get_status(job_id)
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        return ProcessingResponse(**status)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get(
    "/process/metrics",
    summary="Get processing metrics",
    description="Get processing service metrics"
)
async def get_metrics():
    """
    Get processing metrics:
    1. Processing times
    2. Queue sizes
    3. Success rates
    4. Error rates
    5. Quality scores
    """
    try:
        return {
            "processing_time": metrics.processing_time._value.get(),
            "queue_size": metrics.processing_queue_size._value.get(),
            "active_jobs": metrics.processing_active_jobs._value.get(),
            "success_rate": metrics.processing_success_rate._value.get(),
            "error_rate": metrics.processing_error_rate._value.get(),
            "quality_score": metrics.processing_quality_score._value.get()
        }
    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
