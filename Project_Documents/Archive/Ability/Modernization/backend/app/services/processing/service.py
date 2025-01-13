from typing import Dict, List, Optional, AsyncGenerator
import asyncio
import uuid
from datetime import datetime
import json
from PIL import Image
import pytesseract
import numpy as np
import cv2
from app.core.config import config_manager
from app.core.logging import logger
from app.core.monitoring import metrics
from app.services.cdn import cdn_manager

class ProcessingStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingQuality:
    def __init__(self):
        self.resolution: tuple = (0, 0)
        self.dpi: int = 0
        self.color_depth: int = 0
        self.noise_level: float = 0.0
        self.sharpness: float = 0.0
        self.ocr_confidence: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "resolution": self.resolution,
            "dpi": self.dpi,
            "color_depth": self.color_depth,
            "noise_level": self.noise_level,
            "sharpness": self.sharpness,
            "ocr_confidence": self.ocr_confidence
        }

class ProcessingResult:
    def __init__(
        self,
        id: str,
        status: str,
        input_url: str,
        output_urls: Optional[Dict[str, str]] = None,
        quality: Optional[ProcessingQuality] = None,
        error: Optional[str] = None
    ):
        self.id = id
        self.status = status
        self.input_url = input_url
        self.output_urls = output_urls or {}
        self.quality = quality
        self.error = error
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "status": self.status,
            "input_url": self.input_url,
            "output_urls": self.output_urls,
            "quality": self.quality.to_dict() if self.quality else None,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class ProcessingService:
    def __init__(self):
        self._setup_monitoring()
        self.batch_queue = asyncio.Queue()
        self.active_jobs: Dict[str, ProcessingResult] = {}
        self._start_batch_processor()

    def _setup_monitoring(self):
        """Setup monitoring metrics"""
        self.metrics = {
            "processing_time": metrics.processing_time,
            "queue_size": metrics.processing_queue_size,
            "active_jobs": metrics.processing_active_jobs,
            "success_rate": metrics.processing_success_rate,
            "error_rate": metrics.processing_error_rate,
            "quality_score": metrics.processing_quality_score
        }

    def _start_batch_processor(self):
        """Start background batch processor"""
        async def process_batches():
            while True:
                try:
                    batch = []
                    batch_size = await config_manager.get_config(
                        "processing.batch_size"
                    )
                    
                    # Collect batch of jobs
                    while len(batch) < batch_size:
                        try:
                            job = await asyncio.wait_for(
                                self.batch_queue.get(),
                                timeout=1.0
                            )
                            batch.append(job)
                        except asyncio.TimeoutError:
                            break
                    
                    if batch:
                        # Process batch
                        await self._process_batch(batch)
                        
                except Exception as e:
                    logger.error(f"Batch processing error: {e}")
                    await asyncio.sleep(1)

        asyncio.create_task(process_batches())

    async def process_async(
        self,
        input_data: bytes,
        mime_type: str,
        options: Optional[Dict] = None
    ) -> str:
        """Queue item for async processing"""
        job_id = str(uuid.uuid4())
        
        try:
            # Upload input to CDN
            input_url = await self._upload_input(job_id, input_data, mime_type)
            
            # Create job
            result = ProcessingResult(
                id=job_id,
                status=ProcessingStatus.PENDING,
                input_url=input_url
            )
            self.active_jobs[job_id] = result
            
            # Queue for processing
            await self.batch_queue.put({
                "id": job_id,
                "data": input_data,
                "mime_type": mime_type,
                "options": options
            })
            
            self.metrics["queue_size"].inc()
            return job_id
            
        except Exception as e:
            logger.error(f"Job queueing error: {e}")
            self.metrics["error_rate"].inc()
            raise

    async def process_sync(
        self,
        input_data: bytes,
        mime_type: str,
        options: Optional[Dict] = None
    ) -> ProcessingResult:
        """Process item synchronously"""
        job_id = str(uuid.uuid4())
        
        try:
            start_time = datetime.utcnow()
            
            # Upload input
            input_url = await self._upload_input(job_id, input_data, mime_type)
            
            # Process image
            result = await self._process_image(
                job_id,
                input_data,
                input_url,
                options
            )
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics["processing_time"].observe(processing_time)
            self.metrics["success_rate"].inc()
            
            return result
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            self.metrics["error_rate"].inc()
            raise

    async def get_status(self, job_id: str) -> Optional[Dict]:
        """Get job status"""
        result = self.active_jobs.get(job_id)
        return result.to_dict() if result else None

    async def _process_batch(self, batch: List[Dict]):
        """Process batch of jobs"""
        try:
            # Process each job
            for job in batch:
                try:
                    result = await self._process_image(
                        job["id"],
                        job["data"],
                        job["input_url"],
                        job["options"]
                    )
                    self.metrics["success_rate"].inc()
                except Exception as e:
                    logger.error(f"Job processing error: {e}")
                    self.metrics["error_rate"].inc()
                    
            self.metrics["queue_size"].dec(len(batch))
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")

    async def _process_image(
        self,
        job_id: str,
        input_data: bytes,
        input_url: str,
        options: Optional[Dict]
    ) -> ProcessingResult:
        """Process single image"""
        try:
            # Update status
            result = self.active_jobs.get(job_id)
            if result:
                result.status = ProcessingStatus.PROCESSING
                result.updated_at = datetime.utcnow()
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(input_data))
            
            # Analyze quality
            quality = await self._analyze_quality(image)
            
            # Perform OCR
            ocr_result = await self._perform_ocr(image)
            
            # Apply processing options
            processed_image = await self._apply_processing(image, options)
            
            # Upload results
            output_urls = await self._upload_results(
                job_id,
                processed_image,
                ocr_result
            )
            
            # Update result
            if result:
                result.status = ProcessingStatus.COMPLETED
                result.output_urls = output_urls
                result.quality = quality
                result.updated_at = datetime.utcnow()
                
                # Update quality score metric
                self.metrics["quality_score"].observe(
                    quality.ocr_confidence
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            if result:
                result.status = ProcessingStatus.FAILED
                result.error = str(e)
                result.updated_at = datetime.utcnow()
            raise

    async def _analyze_quality(self, image: Image.Image) -> ProcessingQuality:
        """Analyze image quality"""
        quality = ProcessingQuality()
        
        try:
            # Get resolution
            quality.resolution = image.size
            
            # Calculate DPI
            dpi = image.info.get('dpi', (72, 72))
            quality.dpi = int(sum(dpi) / len(dpi))
            
            # Get color depth
            quality.color_depth = image.mode
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Calculate noise level
            quality.noise_level = np.std(img_array) / 255.0
            
            # Calculate sharpness
            laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
            quality.sharpness = np.var(laplacian)
            
            return quality
            
        except Exception as e:
            logger.error(f"Quality analysis error: {e}")
            return quality

    async def _perform_ocr(self, image: Image.Image) -> Dict:
        """Perform OCR on image"""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Perform OCR
            ocr_data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate confidence
            confidence = np.mean([
                conf for conf in ocr_data['conf']
                if conf != -1
            ])
            
            return {
                "text": " ".join(ocr_data['text']),
                "confidence": confidence,
                "words": list(zip(
                    ocr_data['text'],
                    ocr_data['conf']
                ))
            }
            
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "words": []
            }

    async def _apply_processing(
        self,
        image: Image.Image,
        options: Optional[Dict]
    ) -> Image.Image:
        """Apply processing options"""
        if not options:
            return image
            
        try:
            # Resize if needed
            if 'size' in options:
                width, height = options['size']
                image = image.resize((width, height), Image.LANCZOS)
            
            # Convert format if needed
            if 'format' in options:
                format = options['format'].upper()
                if format != image.format:
                    output = io.BytesIO()
                    image.save(output, format=format)
                    image = Image.open(output)
            
            # Apply filters if needed
            if 'filters' in options:
                for filter_name in options['filters']:
                    if hasattr(Image, filter_name):
                        image = image.filter(getattr(Image, filter_name))
            
            return image
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return image

    async def _upload_input(
        self,
        job_id: str,
        data: bytes,
        mime_type: str
    ) -> str:
        """Upload input file to CDN"""
        try:
            urls = await cdn_manager.upload_file(
                f"processing/{job_id}/input",
                data,
                mime_type
            )
            return next(iter(urls.values()))
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise

    async def _upload_results(
        self,
        job_id: str,
        image: Image.Image,
        ocr_result: Dict
    ) -> Dict[str, str]:
        """Upload processing results"""
        try:
            urls = {}
            
            # Upload processed image
            output = io.BytesIO()
            image.save(output, format=image.format)
            image_urls = await cdn_manager.upload_file(
                f"processing/{job_id}/output",
                output.getvalue(),
                f"image/{image.format.lower()}"
            )
            urls["image"] = next(iter(image_urls.values()))
            
            # Upload OCR results
            ocr_urls = await cdn_manager.upload_file(
                f"processing/{job_id}/ocr",
                json.dumps(ocr_result).encode('utf-8'),
                "application/json"
            )
            urls["ocr"] = next(iter(ocr_urls.values()))
            
            return urls
            
        except Exception as e:
            logger.error(f"Results upload error: {e}")
            raise

# Create global processing service
processing_service = ProcessingService()
