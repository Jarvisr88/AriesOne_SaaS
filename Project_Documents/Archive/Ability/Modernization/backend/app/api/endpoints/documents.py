from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from app.services.documents.processor import document_processor
from app.core.logging import logger
from app.core.monitoring import metrics

router = APIRouter()

class DocumentResponse(BaseModel):
    id: str
    urls: dict
    quality: dict
    metrics: dict

class BatchProcessResponse(BaseModel):
    results: List[DocumentResponse]
    failed: List[str]

@router.post(
    "/documents/process",
    response_model=DocumentResponse,
    summary="Process single document",
    description="Process a single document with OCR and quality analysis"
)
async def process_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Process a single document with the following steps:
    1. Convert to PDF if needed
    2. Extract text and perform OCR
    3. Analyze quality
    4. Upload results to CDN
    """
    try:
        content = await file.read()
        result = await document_processor.process_document(
            content=content,
            mime_type=file.content_type
        )
        return DocumentResponse(**result)
    except Exception as e:
        logger.error(f"Document processing error: {e}")
        metrics.doc_processing_errors.inc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post(
    "/documents/batch",
    response_model=BatchProcessResponse,
    summary="Process batch of documents",
    description="Process multiple documents in parallel"
)
async def process_batch(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Process multiple documents in parallel with:
    1. Automatic batch size adjustment
    2. Progress tracking
    3. Error handling per document
    """
    try:
        documents = []
        for file in files:
            content = await file.read()
            documents.append({
                "content": content,
                "mime_type": file.content_type
            })

        results = await document_processor.process_batch(documents)

        # Separate successful and failed results
        successful = []
        failed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append(files[i].filename)
            else:
                successful.append(DocumentResponse(**result))

        return BatchProcessResponse(
            results=successful,
            failed=failed
        )
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        metrics.doc_processing_errors.inc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get(
    "/documents/{doc_id}",
    response_model=DocumentResponse,
    summary="Get document status",
    description="Get processing status and results for a document"
)
async def get_document(doc_id: str):
    """
    Get document processing status and results:
    1. Processing status
    2. URLs to processed files
    3. Quality metrics
    4. Processing metrics
    """
    try:
        # Implementation depends on storage backend
        pass
    except Exception as e:
        logger.error(f"Document retrieval error: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Document {doc_id} not found"
        )

@router.get(
    "/documents/stats",
    summary="Get processing stats",
    description="Get document processing statistics"
)
async def get_stats():
    """
    Get document processing statistics:
    1. Processing times
    2. Success/failure rates
    3. Quality metrics
    4. Resource usage
    """
    try:
        return {
            "processing_time": metrics.doc_processing_time._value.get(),
            "ocr_time": metrics.doc_ocr_time._value.get(),
            "ocr_confidence": metrics.doc_ocr_confidence._value.get(),
            "pages_processed": metrics.doc_pages_processed._value.get(),
            "errors": metrics.doc_processing_errors._value.get(),
            "quality_score": metrics.doc_quality_score._value.get()
        }
    except Exception as e:
        logger.error(f"Stats retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
