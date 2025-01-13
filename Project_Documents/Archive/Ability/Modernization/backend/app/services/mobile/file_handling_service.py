from typing import Dict, List, Optional, BinaryIO
from datetime import datetime
import hashlib
import mimetypes
import os
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.core.logging import logger
from app.models.mobile import (
    MobileFile,
    FileChunk,
    FileSync,
    FilePermission
)

class FileHandlingService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db
        self.chunk_size = 1024 * 1024  # 1MB
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.storage_path = settings.MOBILE_FILES_PATH
        self.supported_types = [
            "image/*",
            "video/*",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]

    async def upload_file(
        self,
        file: UploadFile,
        user_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Upload file for mobile access"""
        try:
            # Validate file
            await self._validate_file(file)
            
            # Calculate file hash
            file_hash = await self._calculate_hash(file)
            
            # Check for existing file
            existing_file = await MobileFile.get(
                hash=file_hash,
                user_id=user_id
            )
            
            if existing_file:
                return {
                    "status": "exists",
                    "file_id": str(existing_file.id)
                }
            
            # Create file record
            mobile_file = await MobileFile.create(
                user_id=user_id,
                filename=file.filename,
                mime_type=file.content_type,
                size=0,  # Will be updated after chunks
                hash=file_hash,
                metadata=metadata or {},
                status="uploading",
                created_at=datetime.now()
            )
            
            # Process file chunks
            total_size = 0
            chunk_number = 0
            
            while True:
                chunk = await file.read(self.chunk_size)
                if not chunk:
                    break
                
                # Store chunk
                await self._store_chunk(
                    mobile_file.id,
                    chunk_number,
                    chunk
                )
                
                total_size += len(chunk)
                chunk_number += 1
            
            # Update file record
            mobile_file.size = total_size
            mobile_file.status = "ready"
            mobile_file.chunks = chunk_number
            await mobile_file.save()
            
            # Create sync record
            await FileSync.create(
                file_id=mobile_file.id,
                user_id=user_id,
                status="pending",
                created_at=datetime.now()
            )
            
            return {
                "status": "uploaded",
                "file_id": str(mobile_file.id),
                "size": total_size,
                "chunks": chunk_number
            }
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            if mobile_file:
                mobile_file.status = "failed"
                mobile_file.error = str(e)
                await mobile_file.save()
            raise HTTPException(status_code=500, detail=str(e))

    async def download_file(
        self,
        file_id: str,
        user_id: str
    ) -> Dict:
        """Get file download info"""
        try:
            # Get file
            file = await MobileFile.get(id=file_id)
            if not file:
                raise ValueError("File not found")
            
            # Check permission
            await self._check_permission(file, user_id)
            
            # Get chunks info
            chunks = await FileChunk.filter(
                file_id=file_id
            ).order_by("number").all()
            
            return {
                "status": "ready",
                "file_id": str(file.id),
                "filename": file.filename,
                "mime_type": file.mime_type,
                "size": file.size,
                "chunks": len(chunks),
                "metadata": file.metadata
            }
        except Exception as e:
            logger.error(f"File download failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_chunk(
        self,
        file_id: str,
        chunk_number: int,
        user_id: str
    ) -> bytes:
        """Get specific file chunk"""
        try:
            # Get file
            file = await MobileFile.get(id=file_id)
            if not file:
                raise ValueError("File not found")
            
            # Check permission
            await self._check_permission(file, user_id)
            
            # Get chunk
            chunk = await FileChunk.get(
                file_id=file_id,
                number=chunk_number
            )
            if not chunk:
                raise ValueError("Chunk not found")
            
            # Read chunk data
            chunk_path = self._get_chunk_path(file_id, chunk_number)
            with open(chunk_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Chunk retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def share_file(
        self,
        file_id: str,
        user_id: str,
        share_with: List[str],
        permissions: List[str]
    ) -> Dict:
        """Share file with other users"""
        try:
            # Get file
            file = await MobileFile.get(id=file_id)
            if not file:
                raise ValueError("File not found")
            
            # Verify ownership
            if file.user_id != user_id:
                raise ValueError("Not file owner")
            
            # Create permissions
            shared_with = []
            for target_user in share_with:
                permission = await FilePermission.create(
                    file_id=file_id,
                    user_id=target_user,
                    permissions=permissions,
                    granted_by=user_id,
                    created_at=datetime.now()
                )
                shared_with.append(str(permission.id))
            
            return {
                "status": "shared",
                "file_id": file_id,
                "shared_with": shared_with
            }
        except Exception as e:
            logger.error(f"File sharing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_file(
        self,
        file_id: str,
        user_id: str
    ) -> Dict:
        """Delete file"""
        try:
            # Get file
            file = await MobileFile.get(id=file_id)
            if not file:
                raise ValueError("File not found")
            
            # Verify ownership
            if file.user_id != user_id:
                raise ValueError("Not file owner")
            
            # Delete chunks
            chunks = await FileChunk.filter(file_id=file_id).all()
            for chunk in chunks:
                chunk_path = self._get_chunk_path(file_id, chunk.number)
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
                await chunk.delete()
            
            # Delete permissions
            await FilePermission.filter(file_id=file_id).delete()
            
            # Delete file record
            await file.delete()
            
            return {
                "status": "deleted",
                "file_id": file_id
            }
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check file size
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > self.max_file_size:
            raise ValueError(
                f"File too large. Maximum size is {self.max_file_size} bytes"
            )
        
        # Check mime type
        mime_type = file.content_type
        if not any(
            mime_type.startswith(supported)
            for supported in self.supported_types
        ):
            raise ValueError(f"Unsupported file type: {mime_type}")

    async def _calculate_hash(self, file: UploadFile) -> str:
        """Calculate file hash"""
        sha256 = hashlib.sha256()
        
        while True:
            chunk = await file.read(self.chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
        
        file.file.seek(0)
        return sha256.hexdigest()

    async def _store_chunk(
        self,
        file_id: str,
        chunk_number: int,
        data: bytes
    ) -> None:
        """Store file chunk"""
        # Create chunk record
        chunk = await FileChunk.create(
            file_id=file_id,
            number=chunk_number,
            size=len(data),
            created_at=datetime.now()
        )
        
        # Store chunk data
        chunk_path = self._get_chunk_path(file_id, chunk_number)
        os.makedirs(os.path.dirname(chunk_path), exist_ok=True)
        
        with open(chunk_path, "wb") as f:
            f.write(data)

    def _get_chunk_path(
        self,
        file_id: str,
        chunk_number: int
    ) -> str:
        """Get chunk file path"""
        return os.path.join(
            self.storage_path,
            file_id,
            f"chunk_{chunk_number}"
        )

    async def _check_permission(
        self,
        file: MobileFile,
        user_id: str
    ) -> None:
        """Check file access permission"""
        if file.user_id == user_id:
            return
        
        permission = await FilePermission.get(
            file_id=file.id,
            user_id=user_id
        )
        
        if not permission:
            raise ValueError("Access denied")
