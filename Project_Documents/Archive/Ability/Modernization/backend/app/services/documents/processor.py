from typing import List, Dict, Optional, AsyncGenerator
import uuid
from datetime import datetime
import asyncio
import pytesseract
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF
from PIL import Image
import io
import numpy as np
from app.core.config import settings
from app.core.logging import logger
from app.core.monitoring import metrics
from app.services.processing.base import BaseProcessor, ProcessingQuality
from app.services.cdn import cdn_manager

class DocumentType:
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    DOC = "application/msword"
    TXT = "text/plain"
    RTF = "application/rtf"
    PNG = "image/png"
    JPEG = "image/jpeg"
    TIFF = "image/tiff"

class DocumentQuality:
    def __init__(self):
        self.dpi: int = 300
        self.ocr_confidence: float = 0.0
        self.text_quality: float = 0.0
        self.image_quality: float = 0.0
        self.structure_score: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "dpi": self.dpi,
            "ocr_confidence": self.ocr_confidence,
            "text_quality": self.text_quality,
            "image_quality": self.image_quality,
            "structure_score": self.structure_score
        }

class DocumentProcessor:
    def __init__(self):
        self.supported_types = {
            DocumentType.PDF,
            DocumentType.DOCX,
            DocumentType.DOC,
            DocumentType.TXT,
            DocumentType.RTF,
            DocumentType.PNG,
            DocumentType.JPEG,
            DocumentType.TIFF
        }
        self._setup_monitoring()

    def _setup_monitoring(self):
        """Setup monitoring metrics"""
        self.metrics = {
            "processing_time": metrics.doc_processing_time,
            "ocr_time": metrics.doc_ocr_time,
            "ocr_confidence": metrics.doc_ocr_confidence,
            "pages_processed": metrics.doc_pages_processed,
            "errors": metrics.doc_processing_errors,
            "quality_score": metrics.doc_quality_score
        }

    async def process_document(
        self,
        content: bytes,
        mime_type: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """Process single document"""
        start_time = datetime.utcnow()
        doc_id = str(uuid.uuid4())

        try:
            if mime_type not in self.supported_types:
                raise ValueError(f"Unsupported document type: {mime_type}")

            # Convert document to PDF if needed
            if mime_type != DocumentType.PDF:
                content = await self._convert_to_pdf(content, mime_type)

            # Extract text and perform OCR
            text_content, ocr_results = await self._extract_text_and_ocr(content)

            # Analyze document quality
            quality = await self._analyze_quality(content, text_content, ocr_results)

            # Upload processed document
            output_urls = await self._upload_results(
                doc_id,
                content,
                text_content,
                ocr_results
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics["processing_time"].observe(processing_time)

            return {
                "id": doc_id,
                "urls": output_urls,
                "quality": quality.to_dict(),
                "metrics": {
                    "processing_time": processing_time,
                    "pages": len(ocr_results)
                }
            }

        except Exception as e:
            logger.error(f"Document processing error: {e}")
            self.metrics["errors"].inc()
            raise

    async def process_batch(
        self,
        documents: List[Dict[str, bytes]],
        options: Optional[Dict] = None
    ) -> List[Dict]:
        """Process batch of documents"""
        tasks = []
        for doc in documents:
            task = asyncio.create_task(
                self.process_document(
                    doc["content"],
                    doc["mime_type"],
                    options
                )
            )
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _convert_to_pdf(
        self,
        content: bytes,
        mime_type: str
    ) -> bytes:
        """Convert document to PDF"""
        if mime_type == DocumentType.PDF:
            return content

        try:
            if mime_type in [DocumentType.PNG, DocumentType.JPEG, DocumentType.TIFF]:
                img = Image.open(io.BytesIO(content))
                pdf_bytes = io.BytesIO()
                img.save(pdf_bytes, format='PDF')
                return pdf_bytes.getvalue()
            else:
                # Use appropriate converter based on mime type
                # Implementation depends on specific requirements
                pass

        except Exception as e:
            logger.error(f"Conversion error: {e}")
            raise

    async def _extract_text_and_ocr(
        self,
        pdf_content: bytes
    ) -> tuple[str, List[Dict]]:
        """Extract text and perform OCR"""
        text_content = ""
        ocr_results = []

        try:
            # Extract text using PyMuPDF
            pdf_doc = fitz.open(stream=pdf_content)
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                text_content += page.get_text()

                # Perform OCR if text extraction yields poor results
                if len(text_content.strip()) < 100:
                    start_time = datetime.utcnow()
                    
                    # Convert PDF page to image
                    pix = page.get_pixmap()
                    img = Image.frombytes(
                        "RGB",
                        [pix.width, pix.height],
                        pix.samples
                    )
                    
                    # Perform OCR
                    ocr_data = pytesseract.image_to_data(
                        img,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    ocr_time = (datetime.utcnow() - start_time).total_seconds()
                    self.metrics["ocr_time"].observe(ocr_time)
                    
                    # Calculate confidence
                    confidence = np.mean(ocr_data['conf'])
                    self.metrics["ocr_confidence"].observe(confidence)
                    
                    ocr_results.append({
                        "page": page_num + 1,
                        "text": ocr_data['text'],
                        "confidence": confidence
                    })

            self.metrics["pages_processed"].inc(pdf_doc.page_count)
            return text_content, ocr_results

        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            raise

    async def _analyze_quality(
        self,
        content: bytes,
        text_content: str,
        ocr_results: List[Dict]
    ) -> DocumentQuality:
        """Analyze document quality"""
        quality = DocumentQuality()

        try:
            # Analyze text quality
            if text_content:
                words = text_content.split()
                quality.text_quality = min(1.0, len(words) / 1000)

            # Analyze OCR quality
            if ocr_results:
                confidences = [r['confidence'] for r in ocr_results]
                quality.ocr_confidence = np.mean(confidences)

            # Analyze image quality
            pdf_doc = fitz.open(stream=content)
            image_qualities = []
            for page in pdf_doc:
                for img in page.get_images():
                    xref = img[0]
                    image = pdf_doc.extract_image(xref)
                    pil_image = Image.open(io.BytesIO(image["image"]))
                    
                    # Calculate image quality metrics
                    width, height = pil_image.size
                    quality.dpi = int(width / 8.5)  # Assuming letter size
                    
                    # Calculate image sharpness
                    img_array = np.array(pil_image.convert('L'))
                    laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
                    sharpness = np.var(laplacian)
                    image_qualities.append(min(1.0, sharpness / 1000))

            if image_qualities:
                quality.image_quality = np.mean(image_qualities)

            # Calculate overall structure score
            quality.structure_score = np.mean([
                quality.text_quality,
                quality.ocr_confidence,
                quality.image_quality
            ])

            self.metrics["quality_score"].observe(quality.structure_score)
            return quality

        except Exception as e:
            logger.error(f"Quality analysis error: {e}")
            raise

    async def _upload_results(
        self,
        doc_id: str,
        content: bytes,
        text_content: str,
        ocr_results: List[Dict]
    ) -> Dict[str, str]:
        """Upload processed results"""
        try:
            urls = {}

            # Upload original PDF
            pdf_urls = await cdn_manager.upload_file(
                f"documents/{doc_id}/original.pdf",
                content,
                "application/pdf"
            )
            urls["pdf"] = pdf_urls

            # Upload extracted text
            text_urls = await cdn_manager.upload_file(
                f"documents/{doc_id}/text.txt",
                text_content.encode('utf-8'),
                "text/plain"
            )
            urls["text"] = text_urls

            # Upload OCR results
            if ocr_results:
                ocr_urls = await cdn_manager.upload_file(
                    f"documents/{doc_id}/ocr.json",
                    json.dumps(ocr_results).encode('utf-8'),
                    "application/json"
                )
                urls["ocr"] = ocr_urls

            return urls

        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise

# Create global document processor
document_processor = DocumentProcessor()
