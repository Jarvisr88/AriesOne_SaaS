from typing import Dict, Optional, List, AsyncGenerator
import asyncio
from datetime import datetime
import psutil
from app.services.processing.base import (
    ProcessingType,
    ProcessingQuality,
    ProcessingMode,
    ProcessingResult,
    ProcessingError
)
from app.services.processing.image import ImageProcessor
from app.core.config import settings
from app.core.logging import logger
from app.core.monitoring import metrics

class ProcessingManager:
    def __init__(self):
        self.processors: Dict[ProcessingType, BaseProcessor] = {
            ProcessingType.IMAGE: ImageProcessor(),
            # Add other processors here
        }
        self._setup_monitoring()
        self._start_resource_monitoring()

    def _setup_monitoring(self) -> None:
        """Setup monitoring metrics"""
        self.metrics = {
            "queue_size": metrics.processing_queue_size,
            "active_workers": metrics.processing_active_workers,
            "cpu_usage": metrics.processing_cpu_usage,
            "memory_usage": metrics.processing_memory_usage,
            "batch_size": metrics.processing_batch_size
        }

    def _start_resource_monitoring(self) -> None:
        """Start resource monitoring"""
        async def monitor_resources():
            while True:
                try:
                    # Monitor CPU usage
                    cpu_percent = psutil.cpu_percent()
                    self.metrics["cpu_usage"].set(cpu_percent)
                    
                    # Monitor memory usage
                    memory = psutil.Process().memory_info()
                    self.metrics["memory_usage"].set(memory.rss)
                    
                    # Adjust batch size based on resource usage
                    self._adjust_batch_size(cpu_percent)
                    
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"Resource monitoring error: {e}")
                
        asyncio.create_task(monitor_resources())

    def _adjust_batch_size(self, cpu_percent: float) -> None:
        """Adjust batch size based on CPU usage"""
        if cpu_percent > 80:
            settings.PROCESSING_BATCH_SIZE = max(
                1,
                settings.PROCESSING_BATCH_SIZE - 1
            )
        elif cpu_percent < 50:
            settings.PROCESSING_BATCH_SIZE = min(
                100,
                settings.PROCESSING_BATCH_SIZE + 1
            )
        
        self.metrics["batch_size"].set(settings.PROCESSING_BATCH_SIZE)

    async def process(
        self,
        processing_type: ProcessingType,
        input_data: bytes,
        quality: ProcessingQuality = ProcessingQuality.AUTO,
        mode: ProcessingMode = ProcessingMode.SYNC,
        options: Optional[Dict] = None
    ) -> ProcessingResult:
        """Process single item"""
        processor = self.processors.get(processing_type)
        if not processor:
            raise ProcessingError(f"Unsupported type: {processing_type}")
            
        try:
            if mode == ProcessingMode.SYNC:
                return await processor.process_single(
                    input_data,
                    quality,
                    options
                )
            else:
                # Add to processing queue
                return await self._queue_processing(
                    processor,
                    input_data,
                    quality,
                    options
                )
        except Exception as e:
            logger.error(f"Processing error: {e}")
            raise ProcessingError(f"Processing failed: {e}")

    async def process_batch(
        self,
        processing_type: ProcessingType,
        input_items: List[bytes],
        quality: ProcessingQuality = ProcessingQuality.AUTO,
        options: Optional[Dict] = None
    ) -> List[ProcessingResult]:
        """Process batch of items"""
        processor = self.processors.get(processing_type)
        if not processor:
            raise ProcessingError(f"Unsupported type: {processing_type}")
            
        try:
            # Split into smaller batches based on current batch size
            batch_size = settings.PROCESSING_BATCH_SIZE
            batches = [
                input_items[i:i + batch_size]
                for i in range(0, len(input_items), batch_size)
            ]
            
            results = []
            for batch in batches:
                batch_results = await processor.process_batch(
                    batch,
                    quality,
                    options
                )
                results.extend(batch_results)
                
            return results
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            raise ProcessingError(f"Batch processing failed: {e}")

    async def process_stream(
        self,
        processing_type: ProcessingType,
        input_stream: asyncio.StreamReader,
        quality: ProcessingQuality = ProcessingQuality.AUTO,
        options: Optional[Dict] = None
    ) -> AsyncGenerator[ProcessingResult, None]:
        """Process streaming data"""
        processor = self.processors.get(processing_type)
        if not processor:
            raise ProcessingError(f"Unsupported type: {processing_type}")
            
        try:
            async for result in processor.process_stream(
                input_stream,
                quality,
                options
            ):
                yield result
        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            raise ProcessingError(f"Stream processing failed: {e}")

    async def _queue_processing(
        self,
        processor: BaseProcessor,
        input_data: bytes,
        quality: ProcessingQuality,
        options: Optional[Dict]
    ) -> ProcessingResult:
        """Queue item for processing"""
        try:
            # Update queue size metric
            self.metrics["queue_size"].inc()
            
            # Process in background
            result = await asyncio.create_task(
                processor.process_single(input_data, quality, options)
            )
            
            # Update queue size metric
            self.metrics["queue_size"].dec()
            
            return result
        except Exception as e:
            logger.error(f"Queue processing error: {e}")
            self.metrics["queue_size"].dec()
            raise ProcessingError(f"Queue processing failed: {e}")

    def get_stats(self) -> Dict:
        """Get processing statistics"""
        return {
            "queue_size": self.metrics["queue_size"]._value.get(),
            "active_workers": self.metrics["active_workers"]._value.get(),
            "cpu_usage": self.metrics["cpu_usage"]._value.get(),
            "memory_usage": self.metrics["memory_usage"]._value.get(),
            "batch_size": settings.PROCESSING_BATCH_SIZE
        }

# Create global processing manager
processing_manager = ProcessingManager()
