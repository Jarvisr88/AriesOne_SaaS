"""
File Repository Module

This module provides data access for file operations.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.file import FileMetadata
from ..models.database.file_models import FileMetadataDB

class FileRepository:
    """Repository for file data access."""

    async def create_file(
        self,
        file: FileMetadata,
        db: AsyncSession
    ) -> FileMetadata:
        """
        Create file metadata.
        
        Args:
            file: File metadata
            db: Database session
        
        Returns:
            Created file metadata
        """
        file_db = FileMetadataDB(
            file_id=file.file_id,
            filename=file.filename,
            original_filename=file.original_filename,
            content_type=file.content_type,
            size=file.size,
            user_id=file.user_id,
            metadata=file.metadata
        )

        db.add(file_db)
        await db.commit()
        await db.refresh(file_db)

        return FileMetadata.model_validate(file_db)

    async def get_file(
        self,
        file_id: UUID,
        db: AsyncSession
    ) -> Optional[FileMetadata]:
        """
        Get file metadata by ID.
        
        Args:
            file_id: File ID
            db: Database session
        
        Returns:
            File metadata if found
        """
        stmt = select(FileMetadataDB).where(
            FileMetadataDB.file_id == file_id,
            FileMetadataDB.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        file_db = result.scalar_one_or_none()

        if file_db:
            return FileMetadata.model_validate(file_db)
        return None

    async def update_file(
        self,
        file_id: UUID,
        file: FileMetadata,
        db: AsyncSession
    ) -> FileMetadata:
        """
        Update file metadata.
        
        Args:
            file_id: File ID
            file: Updated file metadata
            db: Database session
        
        Returns:
            Updated file metadata
        
        Raises:
            ValueError: If file not found
        """
        stmt = select(FileMetadataDB).where(
            FileMetadataDB.file_id == file_id,
            FileMetadataDB.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        file_db = result.scalar_one_or_none()

        if not file_db:
            raise ValueError(f"File {file_id} not found")

        # Update fields
        file_db.filename = file.filename
        file_db.original_filename = file.original_filename
        file_db.content_type = file.content_type
        file_db.size = file.size
        file_db.metadata = file.metadata

        await db.commit()
        await db.refresh(file_db)

        return FileMetadata.model_validate(file_db)

    async def delete_file(
        self,
        file_id: UUID,
        db: AsyncSession
    ) -> None:
        """
        Delete file metadata.
        
        Args:
            file_id: File ID
            db: Database session
        
        Raises:
            ValueError: If file not found
        """
        stmt = select(FileMetadataDB).where(
            FileMetadataDB.file_id == file_id,
            FileMetadataDB.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        file_db = result.scalar_one_or_none()

        if not file_db:
            raise ValueError(f"File {file_id} not found")

        file_db.deleted_at = datetime.utcnow()
        await db.commit()

    async def list_files(
        self,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession
    ) -> list[FileMetadata]:
        """
        List files with optional filtering.
        
        Args:
            user_id: Optional user ID filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            db: Database session
        
        Returns:
            List of file metadata
        """
        query = select(FileMetadataDB).where(
            FileMetadataDB.deleted_at.is_(None)
        )

        if user_id:
            query = query.where(FileMetadataDB.user_id == user_id)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        files_db = result.scalars().all()

        return [FileMetadata.model_validate(f) for f in files_db]
