from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
from datetime import datetime
from PIL import Image
import numpy as np
import tensorflow as tf
from app.core.config import settings
from app.core.logging import logger
from app.core.monitoring import metrics
from app.services.cdn import cdn_manager

class ProcessingType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"

class ProcessingQuality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AUTO = "auto"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingMode(str, Enum):
    SYNC = "sync"
    ASYNC = "async"
    BATCH = "batch"
    STREAM = "stream"

class ProcessingResult:
    def __init__(
        self,
        id: str,
        status: ProcessingStatus,
        output_urls: Optional[Dict[str, str]] = None,
        error: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.status = status
        self.output_urls = output_urls or {}
        self.error = error
        self.metrics = metrics or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class QualityMetrics:
    def __init__(self):
        self.sharpness: float = 0.0
        self.noise_level: float = 0.0
        self.compression_ratio: float = 0.0
        self.color_accuracy: float = 0.0
        self.resolution_score: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "sharpness": self.sharpness,
            "noise_level": self.noise_level,
            "compression_ratio": self.compression_ratio,
            "color_accuracy": self.color_accuracy,
            "resolution_score": self.resolution_score
        }

class BaseProcessor(ABC):
    def __init__(self):
        self.model = self._load_ai_model()
        self._setup_monitoring()

    def _setup_monitoring(self) -> None:
        """Setup monitoring metrics"""
        self.metrics = {
            "processing_time": metrics.processing_time,
            "processing_errors": metrics.processing_errors,
            "quality_score": metrics.quality_score,
            "batch_size": metrics.batch_size,
            "memory_usage": metrics.memory_usage
        }

    @abstractmethod
    def _load_ai_model(self) -> tf.keras.Model:
        """Load AI model for processing"""
        pass

    @abstractmethod
    async def process_single(
        self,
        input_data: bytes,
        quality: ProcessingQuality,
        options: Optional[Dict] = None
    ) -> ProcessingResult:
        """Process single item"""
        pass

    @abstractmethod
    async def process_batch(
        self,
        input_items: List[bytes],
        quality: ProcessingQuality,
        options: Optional[Dict] = None
    ) -> List[ProcessingResult]:
        """Process batch of items"""
        pass

    @abstractmethod
    async def process_stream(
        self,
        input_stream: asyncio.StreamReader,
        quality: ProcessingQuality,
        options: Optional[Dict] = None
    ) -> AsyncGenerator[ProcessingResult, None]:
        """Process streaming data"""
        pass

    async def analyze_quality(self, data: bytes) -> QualityMetrics:
        """Analyze input quality"""
        metrics = QualityMetrics()
        
        try:
            # Convert to numpy array for analysis
            img = Image.open(io.BytesIO(data))
            img_array = np.array(img)
            
            # Calculate sharpness using Laplacian
            laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
            metrics.sharpness = np.var(laplacian)
            
            # Calculate noise level
            noise = np.std(img_array)
            metrics.noise_level = noise / 255.0
            
            # Calculate compression ratio
            original_size = len(data)
            compressed = io.BytesIO()
            img.save(compressed, format='JPEG', quality=85)
            compressed_size = len(compressed.getvalue())
            metrics.compression_ratio = compressed_size / original_size
            
            # Calculate color accuracy
            if len(img_array.shape) == 3:
                metrics.color_accuracy = np.mean(np.std(img_array, axis=(0,1)))
            
            # Calculate resolution score
            resolution = img.size[0] * img.size[1]
            metrics.resolution_score = min(1.0, resolution / (1920 * 1080))
            
            return metrics
        except Exception as e:
            logger.error(f"Quality analysis error: {e}")
            return metrics

    async def optimize_quality(
        self,
        data: bytes,
        target_quality: ProcessingQuality
    ) -> bytes:
        """Optimize quality using AI"""
        try:
            # Convert to tensor
            img = tf.image.decode_image(data)
            img = tf.cast(img, tf.float32) / 255.0
            img = tf.expand_dims(img, 0)
            
            # Apply AI enhancement
            enhanced = self.model(img)
            enhanced = tf.clip_by_value(enhanced, 0, 1)
            enhanced = tf.cast(enhanced * 255, tf.uint8)
            
            # Convert back to bytes
            buffer = tf.io.encode_jpeg(
                enhanced[0],
                quality=self._get_quality_value(target_quality)
            )
            
            return buffer.numpy()
        except Exception as e:
            logger.error(f"Quality optimization error: {e}")
            return data

    def _get_quality_value(self, quality: ProcessingQuality) -> int:
        """Convert quality enum to numeric value"""
        quality_map = {
            ProcessingQuality.LOW: 60,
            ProcessingQuality.MEDIUM: 80,
            ProcessingQuality.HIGH: 95,
            ProcessingQuality.AUTO: 85
        }
        return quality_map.get(quality, 85)

    async def upload_result(
        self,
        data: bytes,
        file_path: str,
        content_type: str
    ) -> Dict[str, str]:
        """Upload processed result to CDN"""
        try:
            return await cdn_manager.upload_file(
                file_path=file_path,
                content=data,
                content_type=content_type
            )
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise

class ProcessingError(Exception):
    """Base exception for processing operations"""
    pass

class QualityAnalysisError(ProcessingError):
    """Error during quality analysis"""
    pass

class OptimizationError(ProcessingError):
    """Error during optimization"""
    pass

class ProcessingTimeoutError(ProcessingError):
    """Error when processing times out"""
    pass
