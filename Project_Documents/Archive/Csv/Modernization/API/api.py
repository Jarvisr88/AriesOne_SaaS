from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Optional, List, Dict, Any
from .models import CsvConfig, CsvParseResult
from .service import CsvService

router = APIRouter(prefix="/api/csv", tags=["CSV"])


@router.post("/parse", response_model=CsvParseResult)
async def parse_csv(
    file: UploadFile = File(...),
    config: Optional[CsvConfig] = None,
    csv_service: CsvService = Depends(),
) -> CsvParseResult:
    """
    Parse a CSV file with optional configuration.
    
    Args:
        file: The CSV file to parse
        config: Optional CSV parsing configuration
        csv_service: CSV service instance
        
    Returns:
        CsvParseResult containing parsed data and any errors
    """
    return await csv_service.process_file(file, config)


@router.post("/validate", response_model=List[str])
async def validate_csv(
    file: UploadFile = File(...),
    required_fields: List[str] = [],
    csv_service: CsvService = Depends(),
) -> List[str]:
    """
    Validate CSV headers against required fields.
    
    Args:
        file: The CSV file to validate
        required_fields: List of required field names
        csv_service: CSV service instance
        
    Returns:
        List of missing required fields
    """
    result = await csv_service.process_file(file)
    if not result.headers:
        raise HTTPException(
            status_code=400,
            detail="CSV file must have headers for validation"
        )
    
    return csv_service.validate_headers(result.headers, required_fields)


@router.post("/transform", response_model=CsvParseResult)
async def transform_csv(
    file: UploadFile = File(...),
    transformations: Dict[str, str] = {},
    csv_service: CsvService = Depends(),
) -> CsvParseResult:
    """
    Parse and transform CSV data.
    
    Args:
        file: The CSV file to transform
        transformations: Dictionary mapping field names to transformation functions
        csv_service: CSV service instance
        
    Returns:
        CsvParseResult with transformed data
    """
    # Create transformation functions from string specifications
    transform_funcs = {}
    for field, transform in transformations.items():
        if transform == "int":
            transform_funcs[field] = int
        elif transform == "float":
            transform_funcs[field] = float
        elif transform == "bool":
            transform_funcs[field] = lambda x: x.lower() == "true"
        elif transform == "strip":
            transform_funcs[field] = str.strip
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown transformation: {transform}"
            )
    
    # Parse and transform the data
    result = await csv_service.process_file(file)
    result.records = csv_service.transform_data(
        result.records, 
        transform_funcs
    )
    
    return result
