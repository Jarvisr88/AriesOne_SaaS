"""
File Service Module

This module provides file management functionality.
"""
import os
from typing import BinaryIO, Optional
from uuid import UUID, uuid4

from azure.storage.blob.aio import BlobServiceClient
from fastapi import HTTPException, UploadFile

from ..repositories.file_repository import FileRepository
from ..models.file import FileMetadata
from ..utils.monitoring import get_logger

class FileService:
    """Service for file operations."""

    def __init__(
        self,
        repository: FileRepository,
        blob_service: BlobServiceClient,
        container_name: str,
        max_size: int,
        allowed_extensions: list[str],
        logger = None
    ):
        """
        Initialize file service.
        
        Args:
            repository: File repository
            blob_service: Azure Blob service client
            container_name: Azure container name
            max_size: Maximum file size in bytes
            allowed_extensions: List of allowed file extensions
            logger: Optional logger instance
        """
        self.repository = repository
        self.blob_service = blob_service
        self.container_name = container_name
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions
        self.logger = logger or get_logger(__name__)

    async def upload_file(
        self,
        file: UploadFile,
        user_id: UUID,
        metadata: Optional[dict] = None
    ) -> FileMetadata:
        """
        Upload file to storage.
        
        Args:
            file: File to upload
            user_id: ID of user uploading file
            metadata: Optional file metadata
        
        Returns:
            File metadata
        
        Raises:
            HTTPException: If file is invalid
        """
        try:
            # Validate file
            await self._validate_file(file)

            # Generate unique filename
            filename = f"{uuid4()}{os.path.splitext(file.filename)[1]}"

            # Upload to Azure Blob Storage
            container_client = self.blob_service.get_container_client(
                self.container_name
            )
            blob_client = container_client.get_blob_client(filename)
            
            contents = await file.read()
            await blob_client.upload_blob(contents)

            # Create file metadata
            file_metadata = FileMetadata(
                filename=filename,
                original_filename=file.filename,
                content_type=file.content_type,
                size=len(contents),
                user_id=user_id,
                metadata=metadata or {}
            )

            # Save metadata to database
            return await self.repository.create_file(file_metadata)

        except Exception as e:
            self.logger.error(f"File upload failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="File upload failed"
            )

    async def download_file(
        self,
        file_id: UUID
    ) -> tuple[BinaryIO, str]:
        """
        Download file from storage.
        
        Args:
            file_id: File ID
        
        Returns:
            Tuple of file stream and filename
        
        Raises:
            HTTPException: If file not found
        """
        try:
            # Get file metadata
            metadata = await self.repository.get_file(file_id)
            if not metadata:
                raise HTTPException(
                    status_code=404,
                    detail="File not found"
                )

            # Get file from Azure Blob Storage
            container_client = self.blob_service.get_container_client(
                self.container_name
            )
            blob_client = container_client.get_blob_client(metadata.filename)
            
            download_stream = await blob_client.download_blob()
            return download_stream, metadata.original_filename

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"File download failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="File download failed"
            )

    async def delete_file(
        self,
        file_id: UUID
    ) -> None:
        """
        Delete file from storage.
        
        Args:
            file_id: File ID
        
        Raises:
            HTTPException: If file not found or deletion fails
        """
        try:
            # Get file metadata
            metadata = await self.repository.get_file(file_id)
            if not metadata:
                raise HTTPException(
                    status_code=404,
                    detail="File not found"
                )

            # Delete from Azure Blob Storage
            container_client = self.blob_service.get_container_client(
                self.container_name
            )
            blob_client = container_client.get_blob_client(metadata.filename)
            await blob_client.delete_blob()

            # Delete metadata from database
            await self.repository.delete_file(file_id)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"File deletion failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="File deletion failed"
            )

    async def _validate_file(
        self,
        file: UploadFile
    ) -> None:
        """
        Validate uploaded file.
        
        Args:
            file: File to validate
        
        Raises:
            HTTPException: If file is invalid
        """
        # Check file size
        if file.size > self.max_size:
            raise HTTPException(
                status_code=400,
                detail="File too large"
            )

        # Check file extension
        ext = os.path.splitext(file.filename)[1].lower().lstrip(".")
        if ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="File type not allowed"
            )
