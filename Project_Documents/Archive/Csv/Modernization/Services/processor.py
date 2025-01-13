"""
Data processing service for CSV operations.
"""
from typing import List, Dict, Any, Optional, Generator
from fastapi import UploadFile
from ..Models.types import (
    RowData,
    Headers,
    ValidationResult,
    ImportStatus,
    ErrorSeverity
)
from ..Models.models import CsvConfig
from ..Models.validators import CsvValidator

class CsvProcessor:
    """CSV data processing service."""
    
    def __init__(self, config: CsvConfig):
        self.config = config
        self.validator = CsvValidator(config)
        self.transformations: Dict[str, callable] = {}

    async def process_stream(
        self,
        file: UploadFile,
        chunk_size: int = 8192
    ) -> Generator[str, None, None]:
        """Process CSV file as a stream."""
        while chunk := await file.read(chunk_size):
            yield chunk.decode()

    async def parse_headers(
        self,
        first_line: str
    ) -> ValidationResult[Headers]:
        """Parse and validate CSV headers."""
        headers = first_line.strip().split(self.config.delimiter)
        headers = [h.strip() for h in headers]
        
        return self.validator.validate_headers(headers)

    async def process_row(
        self,
        row: Dict[str, str],
        row_number: int
    ) -> ValidationResult[RowData]:
        """Process and validate a single row."""
        # Validate row
        validation_result = self.validator.validate_row(row, row_number)
        if not validation_result.is_valid:
            return validation_result

        # Apply transformations
        transformed_row = await self.transform_row(row)
        
        return ValidationResult(True, data=transformed_row)

    async def transform_row(
        self,
        row: Dict[str, str]
    ) -> Dict[str, Any]:
        """Apply configured transformations to row data."""
        transformed = row.copy()
        
        for field, transform in self.transformations.items():
            if field in transformed:
                try:
                    transformed[field] = transform(transformed[field])
                except Exception as e:
                    transformed[field] = None
                    # Log transformation error

        return transformed

    def add_transformation(
        self,
        field: str,
        transform_func: callable
    ):
        """Add a transformation function for a field."""
        self.transformations[field] = transform_func

    def remove_transformation(self, field: str):
        """Remove a transformation function for a field."""
        self.transformations.pop(field, None)

    async def process_chunk(
        self,
        chunk: str,
        headers: Headers,
        start_row: int = 0
    ) -> List[ValidationResult[RowData]]:
        """Process a chunk of CSV data."""
        results = []
        lines = chunk.splitlines()
        
        for i, line in enumerate(lines, start=start_row):
            if not line.strip():
                continue

            # Split line into fields
            fields = line.split(self.config.delimiter)
            fields = [f.strip() for f in fields]

            # Create row dict
            if len(fields) != len(headers):
                results.append(
                    ValidationResult(
                        False,
                        errors=[f"Row {i}: Field count mismatch"]
                    )
                )
                continue

            row = dict(zip(headers, fields))
            result = await self.process_row(row, i)
            results.append(result)

        return results

    def get_default_transformations(self) -> Dict[str, callable]:
        """Get dictionary of default transformation functions."""
        return {
            'int': lambda x: int(x) if x else None,
            'float': lambda x: float(x) if x else None,
            'bool': lambda x: str(x).lower() in ('true', '1', 'yes'),
            'strip': lambda x: x.strip() if x else None,
            'upper': lambda x: x.upper() if x else None,
            'lower': lambda x: x.lower() if x else None
        }

    def apply_default_transformations(self):
        """Apply default transformations based on config."""
        defaults = self.get_default_transformations()
        
        for field, rules in self.config.field_rules.items():
            if 'type' in rules:
                field_type = rules['type']
                if field_type in defaults:
                    self.add_transformation(field, defaults[field_type])

    async def validate_file_size(self, file: UploadFile) -> bool:
        """Validate file size against configured limits."""
        if not self.config.max_file_size:
            return True

        # Get file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset position
        
        return size <= self.config.max_file_size
