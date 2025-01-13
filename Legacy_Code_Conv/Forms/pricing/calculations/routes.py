"""
Price calculation routes module.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from .price_calculator import PriceCalculator, PriceCalculation
from ...auth.login_form import LoginManager
from ...core.database import get_database

router = APIRouter(prefix="/price-calculations", tags=["price-calculations"])

@router.get("/calculate/{price_list_id}/{item_code}")
async def calculate_price(
    price_list_id: int,
    item_code: str,
    quantity: int,
    customer_type: Optional[str] = None,
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
) -> PriceCalculation:
    """Calculate price with all applicable discounts."""
    calculator = PriceCalculator(db)
    calculation = await calculator.calculate_price(
        price_list_id,
        item_code,
        quantity,
        customer_type
    )
    
    # Save price history
    await calculator.save_price_history(
        price_list_id,
        item_code,
        calculation,
        customer_type,
        current_user.username
    )
    
    return calculation

@router.get("/history/{price_list_id}/{item_code}")
async def get_price_history(
    price_list_id: int,
    item_code: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    customer_type: Optional[str] = None,
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Get price calculation history."""
    calculator = PriceCalculator(db)
    return await calculator.price_repository.get_price_history(
        price_list_id,
        item_code,
        start_date,
        end_date,
        customer_type
    )

@router.post("/quantity-breaks/{price_list_id}/{item_code}")
async def add_quantity_break(
    price_list_id: int,
    item_code: str,
    min_quantity: int,
    discount_amount: Decimal,
    max_quantity: Optional[int] = None,
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Add quantity break discount."""
    calculator = PriceCalculator(db)
    
    # Get price list item
    item = await calculator.get_base_price(price_list_id, item_code, min_quantity)
    
    # Add quantity break
    return await calculator.price_repository.create_quantity_break(
        item_id=item.id,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        discount_amount=discount_amount,
        created_by=current_user.username
    )

@router.post("/customer-discounts/{price_list_id}")
async def add_customer_discount(
    price_list_id: int,
    customer_type: str,
    discount_type: str,
    discount_value: Decimal,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Add customer-specific discount."""
    calculator = PriceCalculator(db)
    
    return await calculator.price_repository.create_customer_discount(
        price_list_id=price_list_id,
        customer_type=customer_type,
        discount_type=discount_type,
        discount_value=discount_value,
        start_date=start_date,
        end_date=end_date,
        created_by=current_user.username
    )
