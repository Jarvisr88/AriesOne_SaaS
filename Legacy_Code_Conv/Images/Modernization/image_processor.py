"""
Modern image processing module for AriesOne SaaS.

This module provides high-performance image processing capabilities with caching,
async processing, and cloud storage integration.
"""
import io
import os
from typing import Optional, Tuple, Dict, Any
import asyncio
from PIL import Image, ImageOps
from datetime import datetime
import hashlib
import boto3
from botocore.exceptions import ClientError
import aiofiles
import aiohttp
from fastapi import UploadFile
import logging
from redis import Redis
from .config import settings


class ImageProcessor:
    """Handles image processing operations with caching and cloud storage."""
    
    def __init__(self, redis_client: Redis):
        """Initialize the image processor.
        
        Args:
            redis_client: Redis client for caching
        """
        self.redis = redis_client
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.logger = logging.getLogger(__name__)

    async def process_upload(
        self,
        file: UploadFile,
        company_id: int,
        max_size: Tuple[int, int] = (1920, 1080),
        quality: int = 85
    ) -> Dict[str, Any]:
        """Process and store an uploaded image.
        
        Args:
            file: Uploaded file
            company_id: Company ID for organization
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (1-100)
            
        Returns:
            Dict containing processed image info
        """
        try:
            # Read image data
            content = await file.read()
            image_hash = hashlib.sha256(content).hexdigest()
            
            # Check cache
            cached = await self._get_cached_image(image_hash)
            if cached:
                return cached
            
            # Process image
            image = Image.open(io.BytesIO(content))
            processed = await self._process_image(image, max_size, quality)
            
            # Store in S3
            s3_key = f"companies/{company_id}/images/{image_hash}.jpg"
            await self._store_in_s3(processed, s3_key)
            
            # Store metadata
            metadata = {
                "hash": image_hash,
                "company_id": company_id,
                "original_filename": file.filename,
                "content_type": "image/jpeg",
                "size": len(processed),
                "dimensions": image.size,
                "uploaded_at": datetime.utcnow().isoformat(),
                "s3_key": s3_key,
                "url": f"{settings.CDN_BASE_URL}/{s3_key}"
            }
            
            # Cache metadata
            await self._cache_metadata(image_hash, metadata)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            raise

    async def _process_image(
        self,
        image: Image.Image,
        max_size: Tuple[int, int],
        quality: int
    ) -> bytes:
        """Process image with optimizations.
        
        Args:
            image: PIL Image object
            max_size: Maximum dimensions
            quality: JPEG quality
            
        Returns:
            Processed image bytes
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Auto-orient based on EXIF
        image = ImageOps.exif_transpose(image)
        
        # Resize if needed
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save optimized JPEG
        output = io.BytesIO()
        image.save(
            output,
            format='JPEG',
            quality=quality,
            optimize=True,
            progressive=True
        )
        return output.getvalue()

    async def _store_in_s3(self, image_data: bytes, key: str) -> None:
        """Store image in S3 with retry logic.
        
        Args:
            image_data: Image bytes
            key: S3 object key
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await asyncio.to_thread(
                    self.s3.put_object,
                    Bucket=settings.AWS_BUCKET_NAME,
                    Key=key,
                    Body=image_data,
                    ContentType='image/jpeg',
                    CacheControl='public, max-age=31536000'
                )
                return
            except ClientError as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def _get_cached_image(
        self,
        image_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached image metadata.
        
        Args:
            image_hash: Image hash
            
        Returns:
            Cached metadata if found
        """
        cached = await asyncio.to_thread(
            self.redis.get,
            f"image:{image_hash}"
        )
        if cached:
            return eval(cached.decode('utf-8'))
        return None

    async def _cache_metadata(
        self,
        image_hash: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Cache image metadata.
        
        Args:
            image_hash: Image hash
            metadata: Image metadata
        """
        await asyncio.to_thread(
            self.redis.setex,
            f"image:{image_hash}",
            86400,  # 24 hour cache
            str(metadata)
        )

    async def delete_image(
        self,
        company_id: int,
        image_hash: str
    ) -> None:
        """Delete an image and its cached data.
        
        Args:
            company_id: Company ID
            image_hash: Image hash
        """
        try:
            # Delete from S3
            s3_key = f"companies/{company_id}/images/{image_hash}.jpg"
            await asyncio.to_thread(
                self.s3.delete_object,
                Bucket=settings.AWS_BUCKET_NAME,
                Key=s3_key
            )
            
            # Clear cache
            await asyncio.to_thread(
                self.redis.delete,
                f"image:{image_hash}"
            )
            
        except Exception as e:
            self.logger.error(f"Error deleting image: {str(e)}")
            raise
