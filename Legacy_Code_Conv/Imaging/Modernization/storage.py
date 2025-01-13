"""
Storage management for the imaging service.

Handles S3 operations, CloudFront integration, and backup management.
"""
from typing import Optional, BinaryIO, Dict, Any
import boto3
from botocore.exceptions import ClientError
import aioboto3
import logging
from datetime import datetime, timedelta
from .config import settings


class StorageManager:
    """Manages cloud storage operations."""
    
    def __init__(self):
        """Initialize storage manager."""
        self.logger = logging.getLogger(__name__)
        
        # S3 session
        self.session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # CloudFront client
        self.cloudfront = boto3.client(
            'cloudfront',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    async def upload_image(
        self,
        company_id: int,
        image_id: str,
        file_obj: BinaryIO,
        content_type: str,
        metadata: Dict[str, str]
    ) -> Dict[str, Any]:
        """Upload image to S3 with metadata.
        
        Args:
            company_id: Company identifier
            image_id: Unique image identifier
            file_obj: Image file object
            content_type: Image content type
            metadata: Image metadata
            
        Returns:
            Upload details including URLs
        """
        key = f"companies/{company_id}/images/{image_id}"
        
        try:
            async with self.session.client('s3') as s3:
                # Upload to S3
                await s3.upload_fileobj(
                    file_obj,
                    settings.AWS_BUCKET_NAME,
                    key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'Metadata': metadata,
                        'CacheControl': 'max-age=31536000',  # 1 year
                    }
                )
                
                # Get object details
                response = await s3.head_object(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Key=key
                )
                
                return {
                    'key': key,
                    'size': response['ContentLength'],
                    'etag': response['ETag'],
                    'last_modified': response['LastModified'],
                    's3_url': f"s3://{settings.AWS_BUCKET_NAME}/{key}",
                    'cdn_url': f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{key}"
                }
                
        except ClientError as e:
            self.logger.error(f"Error uploading image: {str(e)}")
            raise

    async def get_image(
        self,
        company_id: int,
        image_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get image details and presigned URL.
        
        Args:
            company_id: Company identifier
            image_id: Image identifier
            
        Returns:
            Image details if found
        """
        key = f"companies/{company_id}/images/{image_id}"
        
        try:
            async with self.session.client('s3') as s3:
                # Get object metadata
                response = await s3.head_object(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Key=key
                )
                
                # Generate presigned URL
                url = await s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.AWS_BUCKET_NAME,
                        'Key': key
                    },
                    ExpiresIn=3600  # 1 hour
                )
                
                return {
                    'key': key,
                    'size': response['ContentLength'],
                    'etag': response['ETag'],
                    'last_modified': response['LastModified'],
                    'metadata': response.get('Metadata', {}),
                    'presigned_url': url,
                    'cdn_url': f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{key}"
                }
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            raise

    async def delete_image(
        self,
        company_id: int,
        image_id: str
    ) -> bool:
        """Delete image from storage.
        
        Args:
            company_id: Company identifier
            image_id: Image identifier
            
        Returns:
            True if deleted
        """
        key = f"companies/{company_id}/images/{image_id}"
        
        try:
            async with self.session.client('s3') as s3:
                # Move to backup if enabled
                if settings.BACKUP_ENABLED:
                    await self._backup_image(company_id, image_id)
                
                # Delete from main bucket
                await s3.delete_object(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Key=key
                )
                
                return True
                
        except ClientError as e:
            self.logger.error(f"Error deleting image: {str(e)}")
            return False

    async def _backup_image(
        self,
        company_id: int,
        image_id: str
    ) -> None:
        """Backup image before deletion.
        
        Args:
            company_id: Company identifier
            image_id: Image identifier
        """
        source_key = f"companies/{company_id}/images/{image_id}"
        backup_key = (
            f"backup/{datetime.utcnow().strftime('%Y/%m/%d')}/"
            f"{company_id}/{image_id}"
        )
        
        try:
            async with self.session.client('s3') as s3:
                # Copy to backup bucket
                await s3.copy_object(
                    CopySource={
                        'Bucket': settings.AWS_BUCKET_NAME,
                        'Key': source_key
                    },
                    Bucket=settings.BACKUP_BUCKET,
                    Key=backup_key
                )
                
        except ClientError as e:
            self.logger.error(f"Error backing up image: {str(e)}")
            raise

    async def cleanup_backups(self) -> None:
        """Clean up old backups based on retention policy."""
        if not settings.BACKUP_ENABLED:
            return
            
        cutoff = datetime.utcnow() - timedelta(
            days=settings.BACKUP_RETENTION_DAYS
        )
        
        try:
            async with self.session.client('s3') as s3:
                paginator = s3.get_paginator('list_objects_v2')
                
                async for page in paginator.paginate(
                    Bucket=settings.BACKUP_BUCKET
                ):
                    for obj in page.get('Contents', []):
                        # Check if object is older than retention period
                        if obj['LastModified'] < cutoff:
                            await s3.delete_object(
                                Bucket=settings.BACKUP_BUCKET,
                                Key=obj['Key']
                            )
                            
        except ClientError as e:
            self.logger.error(f"Error cleaning up backups: {str(e)}")
            raise
