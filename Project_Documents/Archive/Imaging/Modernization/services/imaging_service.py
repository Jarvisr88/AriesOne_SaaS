"""Service for handling image operations and MIME type management."""
import uuid
from datetime import datetime, timedelta
from typing import BinaryIO, List, Optional
from fastapi import UploadFile, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import and_, or_

from ..models.imaging_models import (
    ImageMetadata,
    ImageResponse,
    ImageUploadRequest,
    ImageListResponse,
    MimeType,
    MimeTypeCreate
)


class StorageClient:
    """Client for cloud storage operations."""
    
    def __init__(self, bucket: str):
        """Initialize storage client.
        
        Args:
            bucket: Storage bucket name
        """
        self.bucket = bucket
        self.client = boto3.client('s3')
    
    async def upload_blob(
        self,
        path: str,
        data: BinaryIO,
        content_type: str
    ) -> None:
        """Upload blob to storage.
        
        Args:
            path: Blob path
            data: File data
            content_type: Content type
        """
        try:
            await self.client.upload_fileobj(
                data,
                self.bucket,
                path,
                ExtraArgs={'ContentType': content_type}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def get_signed_url(
        self,
        path: str,
        expiry: timedelta = timedelta(minutes=15)
    ) -> str:
        """Get signed URL for blob.
        
        Args:
            path: Blob path
            expiry: URL expiration time
            
        Returns:
            Signed URL
        """
        try:
            return await self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': path
                },
                ExpiresIn=int(expiry.total_seconds())
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate URL: {str(e)}"
            )
    
    async def delete_blob(self, path: str) -> None:
        """Delete blob from storage.
        
        Args:
            path: Blob path
        """
        try:
            await self.client.delete_object(
                Bucket=self.bucket,
                Key=path
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )


class ImageService:
    """Service for handling image operations."""
    
    def __init__(
        self,
        session: AsyncSession,
        storage: StorageClient
    ):
        """Initialize image service.
        
        Args:
            session: Database session
            storage: Storage client
        """
        self.session = session
        self.storage = storage
    
    async def upload_image(
        self,
        company: str,
        image: UploadFile,
        metadata: ImageUploadRequest
    ) -> ImageResponse:
        """Upload new image.
        
        Args:
            company: Company identifier
            image: Upload file
            metadata: Image metadata
            
        Returns:
            Image response with URL
        """
        # Generate unique ID
        image_id = str(uuid.uuid4())
        
        try:
            # Upload to storage
            blob_path = f"{company}/{image_id}"
            await self.storage.upload_blob(
                blob_path,
                image.file,
                image.content_type
            )
            
            # Save metadata
            db_metadata = ImageMetadata(
                id=image_id,
                company=company,
                filename=image.filename,
                content_type=image.content_type,
                size=image.size,
                created_at=datetime.utcnow()
            )
            self.session.add(db_metadata)
            await self.session.commit()
            
            # Get access URL
            url = await self.storage.get_signed_url(blob_path)
            
            return ImageResponse(
                id=image_id,
                url=url,
                metadata=db_metadata
            )
            
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_image(
        self,
        company: str,
        image_id: str
    ) -> ImageResponse:
        """Get image by ID.
        
        Args:
            company: Company identifier
            image_id: Image identifier
            
        Returns:
            Image response with URL
            
        Raises:
            HTTPException: If image not found
        """
        # Get metadata
        stmt = select(ImageMetadata).where(
            and_(
                ImageMetadata.id == image_id,
                ImageMetadata.company == company,
                ImageMetadata.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        metadata = result.scalar_one_or_none()
        
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Get access URL
        blob_path = f"{company}/{image_id}"
        url = await self.storage.get_signed_url(blob_path)
        
        return ImageResponse(
            id=image_id,
            url=url,
            metadata=metadata
        )
    
    async def delete_image(
        self,
        company: str,
        image_id: str
    ) -> None:
        """Delete image.
        
        Args:
            company: Company identifier
            image_id: Image identifier
            
        Raises:
            HTTPException: If image not found
        """
        # Get metadata
        stmt = select(ImageMetadata).where(
            and_(
                ImageMetadata.id == image_id,
                ImageMetadata.company == company,
                ImageMetadata.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        metadata = result.scalar_one_or_none()
        
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        try:
            # Soft delete metadata
            metadata.deleted_at = datetime.utcnow()
            await self.session.commit()
            
            # Delete from storage
            blob_path = f"{company}/{image_id}"
            await self.storage.delete_blob(blob_path)
            
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def list_images(
        self,
        company: str,
        page: int = 1,
        page_size: int = 20
    ) -> ImageListResponse:
        """List images for company.
        
        Args:
            company: Company identifier
            page: Page number
            page_size: Page size
            
        Returns:
            List of images with pagination
        """
        # Get total count
        count_stmt = select(
            func.count(ImageMetadata.id)
        ).where(
            and_(
                ImageMetadata.company == company,
                ImageMetadata.deleted_at.is_(None)
            )
        )
        total = await self.session.scalar(count_stmt)
        
        # Get page of images
        stmt = select(ImageMetadata).where(
            and_(
                ImageMetadata.company == company,
                ImageMetadata.deleted_at.is_(None)
            )
        ).order_by(
            ImageMetadata.created_at.desc()
        ).offset(
            (page - 1) * page_size
        ).limit(page_size)
        
        result = await self.session.execute(stmt)
        images = result.scalars().all()
        
        return ImageListResponse(
            images=images,
            total=total,
            page=page,
            page_size=page_size
        )
