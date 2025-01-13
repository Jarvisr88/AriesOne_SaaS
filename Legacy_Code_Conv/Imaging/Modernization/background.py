"""
Background task processing for image operations.
"""
from typing import Optional, Dict, Any
import asyncio
from fastapi import BackgroundTasks
import logging
from .storage import StorageManager
from .cache import CacheManager
from .processor import ImageProcessor


class BackgroundManager:
    """Manages background tasks."""
    
    def __init__(self):
        """Initialize background manager."""
        self.logger = logging.getLogger(__name__)
        self.storage = StorageManager()
        self.cache = CacheManager()
        self.processor = ImageProcessor()
        
    async def process_image_async(
        self,
        company_id: int,
        image_id: str,
        original_data: bytes,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Process image asynchronously.
        
        Args:
            company_id: Company identifier
            image_id: Image identifier
            original_data: Original image data
            content_type: Content type
            metadata: Image metadata
        """
        try:
            # Process image
            result = await self.processor.process_image(
                io.BytesIO(original_data)
            )
            
            # Upload processed image
            await self.storage.upload_image(
                company_id,
                f"{image_id}/processed",
                result["data"],
                content_type,
                {
                    **metadata,
                    "processed": "true",
                    "size": str(result["size"]),
                    "format": result["format"]
                }
            )
            
            # Upload thumbnails
            for size, thumb_data in result["thumbnails"].items():
                await self.storage.upload_image(
                    company_id,
                    f"{image_id}/thumb_{size}",
                    io.BytesIO(thumb_data),
                    "image/jpeg",
                    {
                        **metadata,
                        "thumbnail": size,
                        "processed": "true"
                    }
                )
                
            # Update cache
            await self.cache.invalidate_pattern(f"{company_id}/{image_id}*")
            
        except Exception as e:
            self.logger.error(
                f"Background processing error for {image_id}: {str(e)}"
            )
            
    async def cleanup_old_images(
        self,
        company_id: int,
        days: int = 30
    ) -> None:
        """Clean up old processed images.
        
        Args:
            company_id: Company identifier
            days: Age in days
        """
        try:
            # List old images
            old_images = await self.storage.list_old_images(
                company_id,
                days
            )
            
            # Delete in batches
            for batch in self._chunk_list(old_images, 100):
                tasks = []
                for image in batch:
                    tasks.append(
                        self.storage.delete_image(
                            company_id,
                            image["key"]
                        )
                    )
                await asyncio.gather(*tasks)
                
        except Exception as e:
            self.logger.error(f"Cleanup error: {str(e)}")
            
    async def generate_missing_thumbnails(
        self,
        company_id: int
    ) -> None:
        """Generate missing thumbnails for images.
        
        Args:
            company_id: Company identifier
        """
        try:
            # List images without thumbnails
            images = await self.storage.list_images_without_thumbnails(
                company_id
            )
            
            # Process in batches
            for batch in self._chunk_list(images, 10):
                tasks = []
                for image in batch:
                    tasks.append(
                        self._generate_thumbnails(
                            company_id,
                            image["key"]
                        )
                    )
                await asyncio.gather(*tasks)
                
        except Exception as e:
            self.logger.error(
                f"Thumbnail generation error: {str(e)}"
            )
            
    async def _generate_thumbnails(
        self,
        company_id: int,
        image_key: str
    ) -> None:
        """Generate thumbnails for single image.
        
        Args:
            company_id: Company identifier
            image_key: Image key
        """
        try:
            # Get original image
            image_data = await self.storage.get_image_data(
                company_id,
                image_key
            )
            
            if not image_data:
                return
                
            # Process thumbnails
            result = await self.processor.process_image(
                io.BytesIO(image_data)
            )
            
            # Upload thumbnails
            for size, thumb_data in result["thumbnails"].items():
                await self.storage.upload_image(
                    company_id,
                    f"{image_key}/thumb_{size}",
                    io.BytesIO(thumb_data),
                    "image/jpeg",
                    {"thumbnail": size}
                )
                
        except Exception as e:
            self.logger.error(
                f"Thumbnail generation error for {image_key}: {str(e)}"
            )
            
    @staticmethod
    def _chunk_list(lst: list, n: int):
        """Split list into chunks.
        
        Args:
            lst: List to split
            n: Chunk size
            
        Yields:
            List chunks
        """
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
