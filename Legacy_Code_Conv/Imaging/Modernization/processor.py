"""
Image processing module with optimization and transformation capabilities.
"""
from typing import Optional, Tuple, Dict, Any, BinaryIO
from PIL import Image, ImageOps
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from .config import settings


class ImageProcessor:
    """Handles image processing and optimization."""
    
    def __init__(self):
        """Initialize image processor."""
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def process_image(
        self,
        image_data: BinaryIO,
        max_size: Optional[Tuple[int, int]] = None,
        quality: Optional[int] = None,
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process and optimize image.
        
        Args:
            image_data: Image file object
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (1-100)
            format: Output format
            
        Returns:
            Processed image data and metadata
        """
        try:
            # Use defaults if not specified
            max_size = max_size or settings.MAX_IMAGE_SIZE
            quality = quality or settings.IMAGE_QUALITY
            format = format or "JPEG"
            
            # Process image in thread pool
            result = await asyncio.to_thread(
                self._process_image_sync,
                image_data,
                max_size,
                quality,
                format
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Image processing error: {str(e)}")
            raise
            
    def _process_image_sync(
        self,
        image_data: BinaryIO,
        max_size: Tuple[int, int],
        quality: int,
        format: str
    ) -> Dict[str, Any]:
        """Synchronous image processing.
        
        Args:
            image_data: Image file object
            max_size: Maximum dimensions
            quality: JPEG quality
            format: Output format
            
        Returns:
            Processed image data and metadata
        """
        # Open image
        image = Image.open(image_data)
        
        # Extract metadata
        metadata = {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
        }
        
        # Convert colorspace if needed
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        
        # Auto-orient based on EXIF
        image = ImageOps.exif_transpose(image)
        
        # Resize if needed
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
        # Generate thumbnails
        thumbnails = self._generate_thumbnails(image)
        
        # Save optimized image
        output = io.BytesIO()
        image.save(
            output,
            format=format,
            quality=quality,
            optimize=True,
            progressive=True
        )
        output.seek(0)
        
        return {
            "data": output,
            "metadata": metadata,
            "thumbnails": thumbnails,
            "size": output.getbuffer().nbytes,
            "format": format.lower()
        }
        
    def _generate_thumbnails(
        self,
        image: Image.Image
    ) -> Dict[str, bytes]:
        """Generate image thumbnails.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary of thumbnail sizes and data
        """
        thumbnails = {}
        
        for name, size in settings.THUMBNAIL_SIZES.items():
            # Create thumbnail
            thumb = image.copy()
            thumb.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            thumb.save(
                output,
                format="JPEG",
                quality=85,
                optimize=True
            )
            output.seek(0)
            
            thumbnails[name] = output.getvalue()
            
        return thumbnails
        
    async def validate_image(
        self,
        image_data: BinaryIO
    ) -> bool:
        """Validate image file.
        
        Args:
            image_data: Image file object
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If image is invalid
        """
        try:
            # Try to open image
            image = Image.open(image_data)
            image.verify()
            
            # Check format
            if image.format.lower() not in settings.ALLOWED_EXTENSIONS:
                raise ValueError(f"Format {image.format} not allowed")
                
            # Check dimensions
            if (image.size[0] > settings.MAX_IMAGE_SIZE[0] or
                image.size[1] > settings.MAX_IMAGE_SIZE[1]):
                raise ValueError("Image dimensions exceed maximum allowed")
                
            return True
            
        except Exception as e:
            raise ValueError(f"Invalid image: {str(e)}")
            
    async def extract_metadata(
        self,
        image_data: BinaryIO
    ) -> Dict[str, Any]:
        """Extract image metadata.
        
        Args:
            image_data: Image file object
            
        Returns:
            Image metadata
        """
        try:
            image = Image.open(image_data)
            
            metadata = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "dpi": image.info.get("dpi"),
            }
            
            # Extract EXIF if available
            if hasattr(image, "_getexif") and image._getexif():
                exif = image._getexif()
                metadata["exif"] = {
                    ExifTags.TAGS[k]: v
                    for k, v in exif.items()
                    if k in ExifTags.TAGS
                }
                
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata extraction error: {str(e)}")
            return {}
