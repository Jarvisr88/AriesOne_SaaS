"""
Name API Endpoints Module
Provides FastAPI routes for name operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from ..models.name_model import Name, CourtesyTitle
from ..services.name_service import NameService
from typing import List

router = APIRouter(prefix="/api/v1/name", tags=["name"])

@router.post("/validate", response_model=Name)
async def validate_name(
    name: Name,
    service: NameService = Depends()
):
    """
    Validate and standardize name format.
    
    Args:
        name: Name to validate
        service: Name service instance
        
    Returns:
        Validated and standardized name
    """
    try:
        return await service.validate_name(name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/courtesy-titles", response_model=List[CourtesyTitle])
async def get_courtesy_titles():
    """
    Get list of valid courtesy titles.
    
    Returns:
        List of courtesy titles
    """
    return list(CourtesyTitle)

@router.post("/format", response_model=str)
async def format_name(
    name: Name,
    format_type: str = "full",
    service: NameService = Depends()
):
    """
    Format name according to specified format type.
    
    Args:
        name: Name to format
        format_type: Format type (full, formal, initials)
        service: Name service instance
        
    Returns:
        Formatted name string
    """
    try:
        return await service.format_name(name, format_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/parse", response_model=Name)
async def parse_name(
    name_string: str,
    service: NameService = Depends()
):
    """
    Parse name string into structured name.
    
    Args:
        name_string: Full name string to parse
        service: Name service instance
        
    Returns:
        Parsed name object
    """
    try:
        return await service.parse_name(name_string)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
