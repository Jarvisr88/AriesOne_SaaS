from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from ..models.address import Address
from ..models.name import Name
from ..services.map_service import MapService

router = APIRouter(prefix="/controls", tags=["controls"])

async def get_map_service():
    """Dependency to get map service instance"""
    service = MapService()
    # Configure providers here
    return service

@router.post("/address/validate")
async def validate_address(
    address: Address,
    map_service: MapService = Depends(get_map_service)
) -> Dict[str, bool]:
    """
    Validate an address using map service
    
    Parameters:
        address: Address to validate
        map_service: Map service instance
    
    Returns:
        Validation result
    """
    try:
        is_valid = await map_service.validate_address(address)
        return {"valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/address/geocode")
async def geocode_address(
    address: Address,
    provider: str,
    map_service: MapService = Depends(get_map_service)
) -> Dict[str, float]:
    """
    Geocode an address using specified provider
    
    Parameters:
        address: Address to geocode
        provider: Name of map provider to use
        map_service: Map service instance
    
    Returns:
        Coordinates for the address
    """
    try:
        provider_instance = map_service.get_provider(provider)
        return await provider_instance.geocode(address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/map/providers")
async def list_providers(
    map_service: MapService = Depends(get_map_service)
) -> List[str]:
    """
    List available map providers
    
    Parameters:
        map_service: Map service instance
    
    Returns:
        List of provider names
    """
    return map_service.get_providers()

@router.post("/name/format")
async def format_name(
    name: Name,
    format_type: str = "full"
) -> Dict[str, str]:
    """
    Format a name according to specified format
    
    Parameters:
        name: Name to format
        format_type: Type of formatting to apply (full or formal)
    
    Returns:
        Formatted name
    """
    try:
        if format_type == "full":
            formatted = name.to_full_name()
        elif format_type == "formal":
            formatted = name.to_formal_name()
        else:
            raise ValueError(f"Unknown format type: {format_type}")
        
        return {"formatted": formatted}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
