"""OCR service module."""

import os
from typing import Dict, List, Optional
import pytesseract
from PIL import Image
import cv2
import numpy as np
from sqlalchemy.orm import Session
from ..models.document import Document, DocumentPage

class OCRService:
    """Service for handling OCR operations."""

    def __init__(self, db: Session, settings: Dict):
        """Initialize the OCR service."""
        self.db = db
        self.settings = settings
        self.tesseract_config = settings.get('tesseract_config', {})
        self.min_confidence = settings.get('min_confidence', 0.6)
        
        # Configure Tesseract
        if 'tesseract_path' in settings:
            pytesseract.pytesseract.tesseract_cmd = settings['tesseract_path']

    def process_document(self, document: Document) -> bool:
        """Process all pages in a document with OCR."""
        try:
            for page in document.pages:
                self.process_page(page)
            return True
        except Exception as e:
            print(f"Document OCR failed: {e}")
            return False

    def process_page(self, page: DocumentPage) -> bool:
        """Process a single page with OCR."""
        try:
            # Load and preprocess image
            img = self._load_image(page.storage_path)
            processed_img = self._preprocess_image(img)

            # Perform OCR
            ocr_data = self._perform_ocr(processed_img)
            
            # Update page with OCR results
            page.ocr_text = ocr_data['text']
            page.ocr_confidence = ocr_data['confidence']
            page.metadata = {
                **page.metadata if page.metadata else {},
                'ocr_details': ocr_data['details']
            }
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Page OCR failed: {e}")
            return False

    def _load_image(self, image_path: str) -> np.ndarray:
        """Load and prepare image for OCR."""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        return img

    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to get black and white image
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary)

        # Deskew if needed
        angle = self._get_skew_angle(denoised)
        if abs(angle) > 0.5:
            denoised = self._rotate_image(denoised, angle)

        return denoised

    def _get_skew_angle(self, img: np.ndarray) -> float:
        """Calculate the skew angle of the image."""
        coords = np.column_stack(np.where(img > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        return angle

    def _rotate_image(self, img: np.ndarray, angle: float) -> np.ndarray:
        """Rotate the image by the given angle."""
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            img, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated

    def _perform_ocr(self, img: np.ndarray) -> Dict:
        """Perform OCR on the preprocessed image."""
        try:
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(
                img, 
                output_type=pytesseract.Output.DICT,
                config=self._get_tesseract_config()
            )

            # Extract text and confidence
            text_parts = []
            confidences = []
            details = []

            for i in range(len(ocr_data['text'])):
                if int(ocr_data['conf'][i]) > 0:  # Filter out low confidence
                    text = ocr_data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        conf = float(ocr_data['conf'][i]) / 100.0
                        confidences.append(conf)
                        details.append({
                            'text': text,
                            'confidence': conf,
                            'bbox': {
                                'x': ocr_data['left'][i],
                                'y': ocr_data['top'][i],
                                'width': ocr_data['width'][i],
                                'height': ocr_data['height'][i]
                            },
                            'line_num': ocr_data['line_num'][i],
                            'word_num': ocr_data['word_num'][i]
                        })

            # Calculate overall confidence
            avg_confidence = (
                sum(confidences) / len(confidences) 
                if confidences else 0.0
            )

            return {
                'text': ' '.join(text_parts),
                'confidence': avg_confidence,
                'details': details
            }

        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")

    def _get_tesseract_config(self) -> str:
        """Get Tesseract configuration string."""
        config_parts = []
        
        # Add language configuration
        if 'lang' in self.tesseract_config:
            config_parts.append(f"-l {self.tesseract_config['lang']}")
        
        # Add PSM mode
        psm = self.tesseract_config.get('psm', 3)
        config_parts.append(f"--psm {psm}")
        
        # Add other configurations
        for key, value in self.tesseract_config.get('params', {}).items():
            config_parts.append(f"-c {key}={value}")
        
        return ' '.join(config_parts)

    def validate_results(self, text: str, confidence: float) -> bool:
        """Validate OCR results."""
        if not text.strip():
            return False
        
        if confidence < self.min_confidence:
            return False
            
        return True
