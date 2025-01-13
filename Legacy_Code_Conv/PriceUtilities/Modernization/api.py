"""
API endpoints for the Price Utilities module.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .services import PriceService, ICDCodeService, PriceCalculationService
from .models import (
    PriceListItem, PriceUpdate, ICDCode, PriceParameter,
    PriceCalculationRule, PriceType, PriceCategory
)
from .auth import get_current_user, User
from .monitoring import monitor

router = APIRouter(prefix="/api/price-utilities", tags=["price-utilities"])

@router.get("/price-list", response_model=List[PriceListItem])
@monitor()
async def get_price_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    filters: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get price list with pagination and filtering."""
    service = PriceService(db)
    return await service.get_price_list(
        company_id=current_user.company_id,
        page=page,
        page_size=page_size,
        filters=filters
    )

@router.post("/price-list/update", response_model=List[PriceListItem])
@monitor()
async def update_prices(
    update: PriceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update prices in bulk."""
    service = PriceService(db)
    return await service.update_prices(update, current_user.id)

@router.get("/icd-codes", response_model=List[ICDCode])
@monitor()
async def get_icd_codes(
    code_type: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get ICD codes with pagination and search."""
    service = ICDCodeService(db)
    return await service.get_icd_codes(
        code_type=code_type,
        page=page,
        page_size=page_size,
        search=search
    )

@router.post("/icd-codes/update", response_model=List[ICDCode])
@monitor()
async def update_icd_codes(
    codes: List[ICDCode],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update ICD codes in bulk."""
    service = ICDCodeService(db)
    return await service.update_icd_codes(codes, current_user.id)

@router.post("/calculate-price")
@monitor()
async def calculate_price(
    base_price: float,
    price_type: PriceType,
    price_category: PriceCategory,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate price based on rules."""
    service = PriceCalculationService(db)
    return await service.calculate_price(
        base_price=base_price,
        company_id=current_user.company_id,
        price_type=price_type,
        price_category=price_category
    )

@router.get("/parameters", response_model=List[PriceParameter])
@monitor()
async def get_parameters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get price parameters."""
    query = select(PriceParameter).where(
        PriceParameter.company_id == current_user.company_id,
        PriceParameter.is_active == True
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/parameters", response_model=PriceParameter)
@monitor()
async def create_parameter(
    parameter: PriceParameter,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create price parameter."""
    parameter.company_id = current_user.company_id
    parameter.created_by = current_user.id
    parameter.updated_by = current_user.id
    db.add(parameter)
    await db.commit()
    return parameter

@router.get("/calculation-rules", response_model=List[PriceCalculationRule])
@monitor()
async def get_calculation_rules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get price calculation rules."""
    query = select(PriceCalculationRule).where(
        PriceCalculationRule.company_id == current_user.company_id,
        PriceCalculationRule.is_active == True
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/calculation-rules", response_model=PriceCalculationRule)
@monitor()
async def create_calculation_rule(
    rule: PriceCalculationRule,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create price calculation rule."""
    rule.company_id = current_user.company_id
    rule.created_by = current_user.id
    rule.updated_by = current_user.id
    db.add(rule)
    await db.commit()
    return rule
