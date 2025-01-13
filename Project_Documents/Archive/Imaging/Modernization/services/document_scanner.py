"""Document scanning service module."""

import os
from typing import Dict, List, Optional, BinaryIO
from datetime import datetime
import cv2
import numpy as np
from sqlalchemy.orm import Session
from ..models.document import Document, DocumentPage, DocumentQualityCheck

class DocumentScanner:
    """Service for handling document scanning operations."""

    def __init__(self, db: Session, settings: Dict):
        """Initialize the document scanner."""
        self.db = db
        self.settings = settings
        self.min_dpi = settings.get('min_dpi', 300)
        self.quality_threshold = settings.get('quality_threshold', 0.8)
        self.supported_formats = settings.get('supported_formats', ['jpg', 'png', 'tiff'])

    def scan_document(self, device_id: str, options: Dict) -> Document:
        """Scan a document using the specified device."""
        # Initialize scanner
        scanner = self._initialize_scanner(device_id)
        
        # Create document record
        document = Document(
            original_filename=f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            mime_type="image/tiff",
            resolution_dpi=options.get('dpi', self.min_dpi)
        )
        self.db.add(document)
        self.db.commit()

        try:
            # Scan pages
            pages = self._scan_pages(scanner, options)
            
            # Process and store pages
            for idx, page_data in enumerate(pages, 1):
                page = self._process_page(document, page_data, idx)
                self._check_quality(page)

            document.page_count = len(pages)
            self.db.commit()
            return document

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Scanning failed: {str(e)}")

    def _initialize_scanner(self, device_id: str) -> any:
        """Initialize the scanner device."""
        try:
            # Implementation depends on scanner hardware/SDK
            # This is a placeholder for actual scanner initialization
            scanner = None  # Replace with actual scanner initialization
            if not scanner:
                raise Exception(f"Failed to initialize scanner: {device_id}")
            return scanner
        except Exception as e:
            raise Exception(f"Scanner initialization failed: {str(e)}")

    def _scan_pages(self, scanner: any, options: Dict) -> List[bytes]:
        """Scan multiple pages from the document feeder."""
        pages = []
        try:
            while True:
                # Scan page
                page_data = self._scan_single_page(scanner, options)
                if not page_data:
                    break
                pages.append(page_data)

                # Check if we've reached the page limit
                if options.get('max_pages') and len(pages) >= options['max_pages']:
                    break

            return pages
        except Exception as e:
            raise Exception(f"Page scanning failed: {str(e)}")

    def _scan_single_page(self, scanner: any, options: Dict) -> Optional[bytes]:
        """Scan a single page with the given options."""
        try:
            # Implementation depends on scanner hardware/SDK
            # This is a placeholder for actual scanning logic
            # Return raw page data
            return None  # Replace with actual scanning
        except Exception as e:
            raise Exception(f"Single page scan failed: {str(e)}")

    def _process_page(self, document: Document, page_data: bytes, page_number: int) -> DocumentPage:
        """Process and store a scanned page."""
        try:
            # Convert to OpenCV format for processing
            nparr = np.frombuffer(page_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Basic image processing
            img = self._enhance_image(img)

            # Save processed image
            storage_path = self._save_page_image(document, img, page_number)

            # Create page record
            page = DocumentPage(
                document_id=document.id,
                page_number=page_number,
                storage_path=storage_path,
                width=img.shape[1],
                height=img.shape[0],
                resolution_dpi=document.resolution_dpi
            )
            self.db.add(page)
            self.db.commit()
            return page

        except Exception as e:
            raise Exception(f"Page processing failed: {str(e)}")

    def _enhance_image(self, img: np.ndarray) -> np.ndarray:
        """Enhance the scanned image quality."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply adaptive thresholding
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
        except Exception as e:
            raise Exception(f"Image enhancement failed: {str(e)}")

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
        rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, 
                                borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def _save_page_image(self, document: Document, img: np.ndarray, 
                        page_number: int) -> str:
        """Save the processed page image."""
        try:
            # Create directory if needed
            directory = os.path.join(self.settings['storage_path'], 
                                   str(document.id))
            os.makedirs(directory, exist_ok=True)

            # Save image
            filename = f"page_{page_number}.tiff"
            path = os.path.join(directory, filename)
            cv2.imwrite(path, img, [cv2.IMWRITE_TIFF_COMPRESSION, 1])
            return path
        except Exception as e:
            raise Exception(f"Failed to save page image: {str(e)}")

    def _check_quality(self, page: DocumentPage) -> None:
        """Perform quality checks on the scanned page."""
        try:
            # Load image
            img = cv2.imread(page.storage_path, cv2.IMREAD_GRAYSCALE)

            # Check resolution
            self._check_resolution(page, img)

            # Check clarity
            self._check_clarity(page, img)

            # Check skew
            self._check_skew(page, img)

            # Check noise
            self._check_noise(page, img)

        except Exception as e:
            raise Exception(f"Quality check failed: {str(e)}")

    def _check_resolution(self, page: DocumentPage, img: np.ndarray) -> None:
        """Check if the image meets resolution requirements."""
        dpi = page.resolution_dpi
        passed = dpi >= self.min_dpi
        
        check = DocumentQualityCheck(
            document_id=page.document_id,
            page_id=page.id,
            check_type='resolution',
            score=dpi / self.min_dpi,
            details={'dpi': dpi, 'min_dpi': self.min_dpi},
            passed=passed
        )
        self.db.add(check)

    def _check_clarity(self, page: DocumentPage, img: np.ndarray) -> None:
        """Check image clarity using Laplacian variance."""
        laplacian = cv2.Laplacian(img, cv2.CV_64F)
        clarity_score = laplacian.var()
        passed = clarity_score > self.settings.get('min_clarity', 100)

        check = DocumentQualityCheck(
            document_id=page.document_id,
            page_id=page.id,
            check_type='clarity',
            score=min(clarity_score / 1000, 1.0),
            details={'clarity_score': clarity_score},
            passed=passed
        )
        self.db.add(check)

    def _check_skew(self, page: DocumentPage, img: np.ndarray) -> None:
        """Check image skew angle."""
        angle = self._get_skew_angle(img)
        passed = abs(angle) < self.settings.get('max_skew', 1.0)

        check = DocumentQualityCheck(
            document_id=page.document_id,
            page_id=page.id,
            check_type='skew',
            score=1.0 - (abs(angle) / 45.0),
            details={'angle': angle},
            passed=passed
        )
        self.db.add(check)

    def _check_noise(self, page: DocumentPage, img: np.ndarray) -> None:
        """Check image noise level."""
        # Calculate noise using standard deviation in smooth areas
        blur = cv2.GaussianBlur(img, (5, 5), 0)
        noise = cv2.absdiff(img, blur)
        noise_level = noise.std()
        passed = noise_level < self.settings.get('max_noise', 10.0)

        check = DocumentQualityCheck(
            document_id=page.document_id,
            page_id=page.id,
            check_type='noise',
            score=1.0 - (noise_level / 50.0),
            details={'noise_level': float(noise_level)},
            passed=passed
        )
        self.db.add(check)
