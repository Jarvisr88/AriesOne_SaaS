"""
API routes for PriceUtilities Module.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime

from .models import (
    PriceUpdateRequest,
    BulkPriceUpdateRequest,
    PriceCalculationRequest,
    AuditQueryParams,
    ErrorResponse
)
from ..services.price_calculation_service import PriceCalculationService
from ..services.update_processing_service import UpdateProcessingService
from ..services.validation_service import ValidationService, ValidationError
from ..services.audit_service import AuditService

# Create router
router = APIRouter(prefix="/api/v1/prices", tags=["prices"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/calculate")
async def calculate_price(
    request: PriceCalculationRequest,
    calculation_service: PriceCalculationService = Depends(),
    token: str = Depends(oauth2_scheme)
):
    """Calculate price for an item with given parameters"""
    try:
        result = await calculation_service.calculate_price(
            item_id=request.item_id,
            quantity=request.quantity,
            icd_codes=request.icd_codes or [],
            date=request.calculation_date
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating price"
        )

@router.post("/update")
async def update_price(
    request: PriceUpdateRequest,
    update_service: UpdateProcessingService = Depends(),
    validation_service: ValidationService = Depends(),
    client_request: Request = None,
    token: str = Depends(oauth2_scheme)
):
    """Update price for a single item"""
    try:
        # Validate update
        await validation_service.validate_price_update(request.dict())
        
        # Process update
        result = await update_service.process_single_update(
            update=request.dict(),
            user_id=client_request.state.user_id,
            ip_address=client_request.client.host
        )
        return {"status": "success", "item_id": request.item_id}
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating price"
        )

@router.post("/bulk-update")
async def bulk_update_prices(
    request: BulkPriceUpdateRequest,
    update_service: UpdateProcessingService = Depends(),
    client_request: Request = None,
    token: str = Depends(oauth2_scheme)
):
    """Process bulk price updates"""
    try:
        result = await update_service.process_bulk_update(
            updates=[update.dict() for update in request.updates],
            user_id=client_request.state.user_id,
            ip_address=client_request.client.host
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing bulk update"
        )

@router.get("/audit")
async def get_audit_logs(
    params: AuditQueryParams = Depends(),
    audit_service: AuditService = Depends(),
    token: str = Depends(oauth2_scheme)
):
    """Retrieve audit logs with filtering"""
    try:
        entries = await audit_service.get_entries(
            start_date=params.start_date,
            end_date=params.end_date,
            entity_type=params.entity_type,
            entity_id=params.entity_id,
            action_type=params.action_type,
            user_id=params.user_id,
            limit=params.limit,
            offset=params.offset
        )
        return entries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving audit logs"
        )

@router.get("/audit/{entity_type}/{entity_id}/changes")
async def get_entity_changes(
    entity_type: str,
    entity_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    audit_service: AuditService = Depends(),
    token: str = Depends(oauth2_scheme)
):
    """Get change history for a specific entity"""
    try:
        changes = await audit_service.get_changes_by_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            start_date=start_date,
            end_date=end_date
        )
        return changes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving entity changes"
        )
