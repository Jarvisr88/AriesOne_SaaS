"""
File Management System

Provides a unified interface for file operations across different storage backends.
"""
from datetime import datetime, timedelta
import hashlib
import mimetypes
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional, Union
import aiofiles
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings, generate_blob_sas, BlobSasPermissions
from fastapi import HTTPException, UploadFile, status
import magic
from pydantic import BaseModel

from ..config import get_settings
from ..monitoring.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

class FileMetadata(BaseModel):
    """File metadata model."""
    filename: str
    content_type: str
    size: int
    hash: str
    created_at: datetime
    last_modified: datetime
    storage_backend: str
    path: str
    metadata: Dict[str, str] = {}

class FileManager:
    """Manages file operations across different storage backends."""
    
    def __init__(self):
        """Initialize file manager."""
        self.blob_service = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_client = self.blob_service.get_container_client(
            settings.AZURE_STORAGE_CONTAINER
        )
        self.local_storage_path = Path(settings.LOCAL_STORAGE_PATH)
        self.local_storage_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file: Union[UploadFile, Path],
        destination: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> FileMetadata:
        """
        Upload file to storage.
        
        Args:
            file: File to upload
            destination: Destination path
            metadata: Optional metadata
            
        Returns:
            File metadata
        """
        try:
            # Determine content type
            if isinstance(file, UploadFile):
                content_type = file.content_type
                file_content = await file.read()
                filename = file.filename
            else:
                content_type = magic.from_file(str(file), mime=True)
                async with aiofiles.open(file, 'rb') as f:
                    file_content = await f.read()
                filename = file.name

            # Calculate hash
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Upload to Azure Blob Storage
            blob_client = self.container_client.get_blob_client(destination)
            
            content_settings = ContentSettings(
                content_type=content_type,
                content_disposition=f'attachment; filename="{filename}"'
            )
            
            await blob_client.upload_blob(
                file_content,
                content_settings=content_settings,
                metadata=metadata,
                overwrite=True
            )
            
            # Get blob properties
            properties = await blob_client.get_blob_properties()
            
            return FileMetadata(
                filename=filename,
                content_type=content_type,
                size=len(file_content),
                hash=file_hash,
                created_at=properties.creation_time,
                last_modified=properties.last_modified,
                storage_backend="azure",
                path=destination,
                metadata=metadata or {}
            )
            
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}"
            )

    async def download_file(
        self,
        path: str,
        destination: Optional[Path] = None
    ) -> Union[bytes, Path]:
        """
        Download file from storage.
        
        Args:
            path: File path
            destination: Optional local destination
            
        Returns:
            File content or local path
        """
        try:
            blob_client = self.container_client.get_blob_client(path)
            
            if destination:
                # Download to file
                destination.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(destination, "wb") as f:
                    async for chunk in blob_client.download_blob().chunks():
                        await f.write(chunk)
                return destination
            else:
                # Return content
                return await blob_client.download_blob().content_as_bytes()
                
        except Exception as e:
            logger.error(f"File download failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File download failed: {str(e)}"
            )

    async def delete_file(self, path: str):
        """
        Delete file from storage.
        
        Args:
            path: File path
        """
        try:
            blob_client = self.container_client.get_blob_client(path)
            await blob_client.delete_blob()
            
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File deletion failed: {str(e)}"
            )

    async def get_file_metadata(self, path: str) -> FileMetadata:
        """
        Get file metadata.
        
        Args:
            path: File path
            
        Returns:
            File metadata
        """
        try:
            blob_client = self.container_client.get_blob_client(path)
            properties = await blob_client.get_blob_properties()
            
            return FileMetadata(
                filename=Path(path).name,
                content_type=properties.content_settings.content_type,
                size=properties.size,
                hash=properties.content_settings.content_md5 or "",
                created_at=properties.creation_time,
                last_modified=properties.last_modified,
                storage_backend="azure",
                path=path,
                metadata=properties.metadata or {}
            )
            
        except Exception as e:
            logger.error(f"Failed to get file metadata: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get file metadata: {str(e)}"
            )

    async def list_files(
        self,
        prefix: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> List[FileMetadata]:
        """
        List files in storage.
        
        Args:
            prefix: Optional path prefix
            max_results: Maximum number of results
            
        Returns:
            List of file metadata
        """
        try:
            files = []
            async for blob in self.container_client.list_blobs(
                name_starts_with=prefix,
                results_per_page=max_results
            ):
                metadata = await self.get_file_metadata(blob.name)
                files.append(metadata)
                
                if max_results and len(files) >= max_results:
                    break
                    
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list files: {str(e)}"
            )

    async def get_file_url(
        self,
        path: str,
        expiry_minutes: int = 60
    ) -> str:
        """
        Get temporary URL for file.
        
        Args:
            path: File path
            expiry_minutes: URL expiry time in minutes
            
        Returns:
            Temporary URL
        """
        try:
            blob_client = self.container_client.get_blob_client(path)
            
            sas_token = generate_blob_sas(
                account_name=blob_client.account_name,
                container_name=blob_client.container_name,
                blob_name=blob_client.blob_name,
                account_key=settings.AZURE_STORAGE_KEY,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(minutes=expiry_minutes)
            )
            
            return f"{blob_client.url}?{sas_token}"
            
        except Exception as e:
            logger.error(f"Failed to generate file URL: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate file URL: {str(e)}"
            )

    async def stream_file(self, path: str) -> AsyncIterator[bytes]:
        """
        Stream file content.
        
        Args:
            path: File path
            
        Yields:
            File chunks
        """
        try:
            blob_client = self.container_client.get_blob_client(path)
            
            async for chunk in blob_client.download_blob().chunks():
                yield chunk
                
        except Exception as e:
            logger.error(f"File streaming failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File streaming failed: {str(e)}"
            )

file_manager = FileManager()
