"""
Price management routes module.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from .price_forms import (
    PriceListForm,
    PriceListItemForm,
    BulkPriceUpdateForm,
    PriceManager
)
from ..auth.login_form import LoginManager
from ...core.database import get_database

router = APIRouter(prefix="/price-lists", tags=["price-lists"])
templates = Jinja2Templates(directory="templates")

@router.get("/create", response_class=HTMLResponse)
async def create_price_list_page(request: Request):
    """Render price list creation page."""
    return templates.TemplateResponse(
        "price_list_create.html",
        {"request": request}
    )

@router.get("/{price_list_id}", response_class=HTMLResponse)
async def price_list_detail_page(request: Request, price_list_id: int):
    """Render price list detail page."""
    return templates.TemplateResponse(
        "price_list_item.html",
        {"request": request, "price_list_id": price_list_id}
    )

@router.post("/")
async def create_price_list(
    form_data: PriceListForm = Depends(PriceListForm.as_form),
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Create new price list."""
    price_manager = PriceManager(db)
    return await price_manager.create_price_list(
        form_data,
        current_user.username
    )

@router.put("/{price_list_id}")
async def update_price_list(
    price_list_id: int,
    form_data: PriceListForm = Depends(PriceListForm.as_form),
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Update price list details."""
    price_manager = PriceManager(db)
    return await price_manager.update_price_list(
        price_list_id,
        form_data,
        current_user.username
    )

@router.post("/items")
async def add_price_list_item(
    form_data: PriceListItemForm = Depends(PriceListItemForm.as_form),
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Add item to price list."""
    price_manager = PriceManager(db)
    return await price_manager.add_price_list_item(
        form_data,
        current_user.username
    )

@router.put("/items/{item_id}")
async def update_price_list_item(
    item_id: int,
    form_data: PriceListItemForm = Depends(PriceListItemForm.as_form),
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Update price list item."""
    price_manager = PriceManager(db)
    return await price_manager.update_price_list_item(
        item_id,
        form_data,
        current_user.username
    )

@router.post("/{price_list_id}/bulk-update")
async def bulk_update_prices(
    price_list_id: int,
    form_data: BulkPriceUpdateForm = Depends(BulkPriceUpdateForm.as_form),
    current_user = Depends(LoginManager.check_active_user),
    db = Depends(get_database)
):
    """Bulk update prices in a price list."""
    price_manager = PriceManager(db)
    return await price_manager.bulk_update_prices(
        form_data,
        current_user.username
    )
