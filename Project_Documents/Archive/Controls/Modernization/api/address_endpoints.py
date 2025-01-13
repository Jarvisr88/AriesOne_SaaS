"""
Address API Endpoints Module
Provides FastAPI routes for address operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.address_model import Address
from ..models.map_model import MapSearchResult
from ..services.address_service import AddressService
from ..services.map_service import MapService

router = APIRouter(prefix="/api/v1/address", tags=["address"])

@router.post("/validate", response_model=Address)
async def validate_address(
    address: Address,
    service: AddressService = Depends()
):
    """
    Validate address and standardize format.
    
    Args:
        address: Address to validate
        service: Address service instance
        
    Returns:
        Validated and standardized address
    """
    try:
        return await service.validate_address(address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/search", response_model=List[MapSearchResult])
async def search_address(
    query: str,
    map_service: MapService = Depends()
):
    """
    Search for addresses using map providers.
    
    Args:
        query: Address search query
        map_service: Map service instance
        
    Returns:
        List of search results from map providers
    """
    try:
        return await map_service.search_address(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/geocode", response_model=MapSearchResult)
async def geocode_address(
    address: Address,
    map_service: MapService = Depends()
):
    """
    Geocode address to get coordinates.
    
    Args:
        address: Address to geocode
        map_service: Map service instance
        
    Returns:
        Geocoding result with coordinates
    """
    try:
        return await map_service.geocode_address(address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reverse-geocode", response_model=List[Address])
async def reverse_geocode(
    latitude: float,
    longitude: float,
    map_service: MapService = Depends()
):
    """
    Reverse geocode coordinates to get addresses.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        map_service: Map service instance
        
    Returns:
        List of possible addresses for coordinates
    """
    try:
        return await map_service.reverse_geocode(latitude, longitude)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
