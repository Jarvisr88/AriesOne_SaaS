from typing import Optional, List, Dict, AsyncGenerator
import io
import uuid
import asyncio
from datetime import datetime
import numpy as np
import tensorflow as tf
from PIL import Image
import cv2
from app.services.processing.base import (
    BaseProcessor,
    ProcessingQuality,
    ProcessingResult,
    ProcessingStatus,
    ProcessingError
)
from app.core.config import settings
from app.core.logging import logger

class ImageProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.supported_formats = {
            'JPEG': 'image/jpeg',
            'PNG': 'image/png',
            'WEBP': 'image/webp',
            'AVIF': 'image/avif'
        }
        self.max_dimension = 4096
        self.chunk_size = 1024 * 1024  # 1MB

    def _load_ai_model(self) -> tf.keras.Model:
        """Load image enhancement model"""
        try:
            # Load pre-trained model for image enhancement
            model = tf.keras.applications.MobileNetV3Large(
                input_shape=(None, None, 3),
                include_top=False,
                weights='imagenet'
            )
            
            # Add custom layers for enhancement
            x = model.output
            x = tf.keras.layers.Conv2D(3, 3, padding='same', activation='relu')(x)
            x = tf.keras.layers.Conv2D(3, 1, activation='sigmoid')(x)
            
            return tf.keras.Model(model.input, x)
        except Exception as e:
            logger.error(f"Model loading error: {e}")
            raise ProcessingError(f"Failed to load AI model: {e}")

    async def process_single(
        self,
        input_data: bytes,
        quality: ProcessingQuality,
        options: Optional[Dict] = None
    ) -> ProcessingResult:
        """Process single image"""
        start_time = datetime.utcnow()
        result_id = str(uuid.uuid4())
        
        try:
            # Analyze input quality
            quality_metrics = await self.analyze_quality(input_data)
            
            # Open image
            img = Image.open(io.BytesIO(input_data))
            
            # Auto-rotate based on EXIF
            img = self._auto_rotate(img)
            
            # Resize if needed
            img = self._resize_image(img, options)
            
            # Convert color space if needed
            img = self._convert_color_space(img, options)
            
            # Optimize quality
            if quality == ProcessingQuality.AUTO:
                quality = self._determine_optimal_quality(quality_metrics)
            
            optimized_data = await self.optimize_quality(
                self._image_to_bytes(img),
                quality
            )
            
            # Convert format if needed
            output_format = options.get('format', img.format)
            if output_format != img.format:
                img = self._convert_format(img, output_format)
            
            # Upload result
            output_urls = await self.upload_result(
                optimized_data,
                f"processed/{result_id}.{output_format.lower()}",
                self.supported_formats[output_format]
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics["processing_time"].observe(processing_time)
            
            return ProcessingResult(
                id=result_id,
                status=ProcessingStatus.COMPLETED,
                output_urls=output_urls,
                metrics={
                    "quality": quality_metrics.to_dict(),
                    "processing_time": processing_time
                }
            )
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            self.metrics["processing_errors"].inc()
            return ProcessingResult(
                id=result_id,
                status=ProcessingStatus.FAILED,
                error=str(e)
            )

    async def process_batch(
        self,
        input_items: List[bytes],
        quality: ProcessingQuality,
        options: Optional[Dict] = None
    ) -> List[ProcessingResult]:
        """Process batch of images"""
        self.metrics["batch_size"].observe(len(input_items))
        
        tasks = [
            self.process_single(item, quality, options)
            for item in input_items
        ]
        
        return await asyncio.gather(*tasks)

    async def process_stream(
        self,
        input_stream: asyncio.StreamReader,
        quality: ProcessingQuality,
        options: Optional[Dict] = None
    ) -> AsyncGenerator[ProcessingResult, None]:
        """Process streaming images"""
        buffer = b""
        
        while True:
            chunk = await input_stream.read(self.chunk_size)
            if not chunk:
                break
            
            buffer += chunk
            
            # Try to find image boundaries
            while True:
                try:
                    # Find next image in buffer
                    img_start = self._find_image_start(buffer)
                    if img_start is None:
                        break
                        
                    img_end = self._find_image_end(
                        buffer[img_start:]
                    )
                    if img_end is None:
                        break
                    
                    # Process image
                    img_data = buffer[img_start:img_start + img_end]
                    result = await self.process_single(
                        img_data,
                        quality,
                        options
                    )
                    yield result
                    
                    # Remove processed image from buffer
                    buffer = buffer[img_start + img_end:]
                except Exception as e:
                    logger.error(f"Stream processing error: {e}")
                    self.metrics["processing_errors"].inc()
                    break

    def _auto_rotate(self, img: Image.Image) -> Image.Image:
        """Auto-rotate image based on EXIF"""
        try:
            return ImageOps.exif_transpose(img)
        except Exception:
            return img

    def _resize_image(
        self,
        img: Image.Image,
        options: Optional[Dict]
    ) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        if not options:
            return img
            
        width = options.get('width')
        height = options.get('height')
        
        if not width and not height:
            return img
            
        ratio = img.width / img.height
        
        if width and height:
            if width / height > ratio:
                width = int(height * ratio)
            else:
                height = int(width / ratio)
        elif width:
            height = int(width / ratio)
        else:
            width = int(height * ratio)
            
        return img.resize((width, height), Image.LANCZOS)

    def _convert_color_space(
        self,
        img: Image.Image,
        options: Optional[Dict]
    ) -> Image.Image:
        """Convert image color space"""
        if not options:
            return img
            
        color_space = options.get('color_space')
        if not color_space:
            return img
            
        if color_space == 'RGB' and img.mode != 'RGB':
            return img.convert('RGB')
        elif color_space == 'RGBA' and img.mode != 'RGBA':
            return img.convert('RGBA')
        elif color_space == 'L' and img.mode != 'L':
            return img.convert('L')
            
        return img

    def _convert_format(
        self,
        img: Image.Image,
        format: str
    ) -> Image.Image:
        """Convert image format"""
        if format not in self.supported_formats:
            raise ProcessingError(f"Unsupported format: {format}")
            
        if img.format == format:
            return img
            
        output = io.BytesIO()
        img.save(output, format=format)
        return Image.open(output)

    def _determine_optimal_quality(
        self,
        metrics: QualityMetrics
    ) -> ProcessingQuality:
        """Determine optimal quality based on metrics"""
        score = (
            metrics.sharpness * 0.3 +
            (1 - metrics.noise_level) * 0.2 +
            (1 - metrics.compression_ratio) * 0.2 +
            metrics.color_accuracy * 0.15 +
            metrics.resolution_score * 0.15
        )
        
        if score < 0.4:
            return ProcessingQuality.LOW
        elif score < 0.7:
            return ProcessingQuality.MEDIUM
        else:
            return ProcessingQuality.HIGH

    def _image_to_bytes(self, img: Image.Image) -> bytes:
        """Convert PIL Image to bytes"""
        output = io.BytesIO()
        img.save(output, format=img.format)
        return output.getvalue()

    def _find_image_start(self, buffer: bytes) -> Optional[int]:
        """Find start of next image in buffer"""
        markers = [b'\xFF\xD8']  # JPEG SOI marker
        
        for marker in markers:
            pos = buffer.find(marker)
            if pos >= 0:
                return pos
        
        return None

    def _find_image_end(self, buffer: bytes) -> Optional[int]:
        """Find end of image in buffer"""
        markers = [b'\xFF\xD9']  # JPEG EOI marker
        
        for marker in markers:
            pos = buffer.find(marker)
            if pos >= 0:
                return pos + len(marker)
        
        return None
