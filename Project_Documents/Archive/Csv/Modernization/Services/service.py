from typing import List, Dict, Any, Optional, BinaryIO
from fastapi import UploadFile, HTTPException
import io
import codecs
from .models import CsvConfig, CsvParseResult
from .reader import CsvReader


class CsvService:
    """Service for handling CSV operations."""

    def __init__(self):
        """Initialize CSV service."""
        self.default_config = CsvConfig()

    async def process_file(
        self, file: UploadFile, config: Optional[CsvConfig] = None
    ) -> CsvParseResult:
        """Process an uploaded CSV file."""
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400, detail="Only CSV files are supported"
            )

        config = config or self.default_config
        reader = CsvReader(config)

        try:
            # Read the file content
            content = await file.read()
            
            # Try to detect the encoding
            encoding = self._detect_encoding(content)
            
            # Create a text IO wrapper with the detected encoding
            text_io = io.TextIOWrapper(
                io.BytesIO(content), 
                encoding=encoding,
                newline=""
            )
            
            # Process the CSV file
            result = reader.read_file(text_io)
            
            return result
            
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Unable to decode the CSV file. Please ensure it's properly encoded."
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error processing CSV file: {str(e)}"
            )

    def _detect_encoding(self, content: bytes) -> str:
        """Detect the encoding of the CSV file."""
        encodings = ['utf-8', 'utf-16', 'ascii', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                content.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
                
        # Default to UTF-8 if no encoding is detected
        return 'utf-8'

    def validate_headers(
        self, 
        headers: List[str], 
        required_fields: List[str]
    ) -> List[str]:
        """Validate CSV headers against required fields."""
        missing_fields = [
            field for field in required_fields 
            if field not in headers
        ]
        
        if missing_fields:
            raise ValueError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
            
        return missing_fields

    def transform_data(
        self, 
        data: List[Dict[str, Any]], 
        transformations: Dict[str, callable]
    ) -> List[Dict[str, Any]]:
        """Apply transformations to CSV data."""
        transformed_data = []
        
        for row in data:
            transformed_row = {}
            
            for field, value in row.items():
                if field in transformations:
                    try:
                        transformed_row[field] = transformations[field](value)
                    except Exception as e:
                        raise ValueError(
                            f"Error transforming field '{field}': {str(e)}"
                        )
                else:
                    transformed_row[field] = value
                    
            transformed_data.append(transformed_row)
            
        return transformed_data
