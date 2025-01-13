"""
Storage service implementation.
"""
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
from app.services.data.base import StorageService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class S3StorageService(StorageService):
    """AWS S3-based storage service implementation."""
    
    def __init__(self):
        self._client = None
        self._is_initialized = False
    
    def initialize(self) -> None:
        """Initialize the S3 client."""
        try:
            self._client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self._is_initialized = True
            logger.info("S3 storage service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize S3 storage service: {str(e)}")
            raise
    
    def validate(self) -> bool:
        """Validate S3 storage configuration."""
        if not self._is_initialized:
            logger.error("S3 storage service not initialized")
            return False
        try:
            # Test bucket access
            self._client.head_bucket(Bucket=settings.STORAGE_BUCKET)
            return True
        except ClientError as e:
            logger.error(f"S3 validation failed: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check S3 storage service health."""
        status = {
            "initialized": self._is_initialized,
            "client_ready": self._client is not None,
        }
        
        if self._is_initialized:
            try:
                # Check bucket accessibility
                self._client.head_bucket(Bucket=settings.STORAGE_BUCKET)
                status["bucket_accessible"] = True
            except ClientError:
                status["bucket_accessible"] = False
        
        return status
    
    def store(self, key: str, data: bytes) -> bool:
        """Store data in S3."""
        if not self._is_initialized:
            raise RuntimeError("S3 storage service not initialized")
        try:
            self._client.put_object(
                Bucket=settings.STORAGE_BUCKET,
                Key=key,
                Body=data
            )
            return True
        except Exception as e:
            logger.error(f"Failed to store data in S3: {str(e)}")
            return False
    
    def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve data from S3."""
        if not self._is_initialized:
            raise RuntimeError("S3 storage service not initialized")
        try:
            response = self._client.get_object(
                Bucket=settings.STORAGE_BUCKET,
                Key=key
            )
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            logger.error(f"Failed to retrieve data from S3: {str(e)}")
            raise
    
    def delete(self, key: str) -> bool:
        """Delete data from S3."""
        if not self._is_initialized:
            raise RuntimeError("S3 storage service not initialized")
        try:
            self._client.delete_object(
                Bucket=settings.STORAGE_BUCKET,
                Key=key
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete data from S3: {str(e)}")
            return False
