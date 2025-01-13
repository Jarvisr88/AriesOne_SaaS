"""
File API Endpoints Module

This module provides FastAPI endpoints for file operations.
"""
from typing import List
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.file import FileMetadata, FileUploadResponse, FileDownloadResponse
from ..services.file_service import FileService
from ..dependencies import get_db, get_current_user, get_file_service

router = APIRouter(prefix="/api/v1/files", tags=["files"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    metadata: dict = None,
    current_user = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: AsyncSession = Depends(get_db)
) -> FileUploadResponse:
    """
    Upload a file.
    
    Args:
        file: File to upload
        metadata: Optional file metadata
        current_user: Current user
        file_service: File service instance
        db: Database session
    
    Returns:
        Upload response with file details
    """
    try:
        file_metadata = await file_service.upload_file(
            file,
            current_user["user_id"],
            metadata,
            db
        )
        return FileUploadResponse(
            file_id=file_metadata.file_id,
            filename=file_metadata.original_filename,
            size=file_metadata.size,
            content_type=file_metadata.content_type,
            metadata=file_metadata.metadata
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/download/{file_id}")
async def download_file(
    file_id: UUID,
    current_user = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """
    Download a file.
    
    Args:
        file_id: File ID
        current_user: Current user
        file_service: File service instance
        db: Database session
    
    Returns:
        File stream
    """
    try:
        stream, filename = await file_service.download_file(file_id, db)
        return StreamingResponse(
            stream,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(
    file_id: UUID,
    current_user = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a file.
    
    Args:
        file_id: File ID
        current_user: Current user
        file_service: File service instance
        db: Database session
    """
    try:
        await file_service.delete_file(file_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=List[FileMetadata])
async def list_files(
    user_id: UUID = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: AsyncSession = Depends(get_db)
) -> List[FileMetadata]:
    """
    List files.
    
    Args:
        user_id: Optional user ID filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current user
        file_service: File service instance
        db: Database session
    
    Returns:
        List of file metadata
    """
    return await file_service.list_files(user_id, skip, limit, db)
