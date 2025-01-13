"""
API routes for the Controls module.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from .models import Address, NameFormat, ChangeTracker, ValidationResult
from .services import AddressService, NameFormatService, ChangeTrackingService
from ..Core.monitoring.logger import Logger
from ..Config.config_manager import ConfigManager

router = APIRouter(prefix="/controls", tags=["controls"])

# Initialize services
config_manager = ConfigManager()
logger = Logger(config_manager)
address_service = AddressService(config_manager.get_config(), logger)
name_service = NameFormatService(logger)
change_service = ChangeTrackingService(logger)

@router.post("/address/validate")
async def validate_address(address: Address) -> ValidationResult:
    """Validate address."""
    return await address_service.validate_address(address)

@router.post("/address/coordinates")
async def get_coordinates(address: Address) -> dict:
    """Get coordinates for address."""
    lat, lng = await address_service.get_coordinates(address)
    if lat is None or lng is None:
        raise HTTPException(status_code=404, detail="Could not get coordinates for address")
    return {"latitude": lat, "longitude": lng}

@router.post("/name/validate")
async def validate_name(name: NameFormat) -> ValidationResult:
    """Validate name format."""
    return name_service.validate_name(name)

@router.post("/name/standardize")
async def standardize_name(name: NameFormat) -> NameFormat:
    """Standardize name format."""
    return name_service.standardize_name(name)

@router.post("/changes/track/{entity_type}/{entity_id}")
async def track_changes(
    entity_type: str,
    entity_id: str,
    changes: List[ChangeTracker]
) -> dict:
    """Track changes to an entity."""
    await change_service.track_change(entity_type, entity_id, changes)
    return {"status": "success", "message": "Changes tracked successfully"}

@router.get("/changes/{entity_type}/{entity_id}")
async def get_changes(
    entity_type: str,
    entity_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[ChangeTracker]:
    """Get change history for an entity."""
    return await change_service.get_change_history(
        entity_type,
        entity_id,
        start_date,
        end_date
    )
