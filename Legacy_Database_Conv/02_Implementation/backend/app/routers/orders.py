"""
Order domain API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..models.order import Order, OrderDetail, SerialTransaction, OrderSurvey
from ..schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse,
    OrderDetailCreate, OrderDetailUpdate, OrderDetailResponse,
    SerialTransactionCreate, SerialTransactionUpdate, SerialTransactionResponse,
    OrderSurveyCreate, OrderSurveyUpdate, OrderSurveyResponse
)
from ..dependencies.database import get_db
from ..services.order import OrderService

router = APIRouter()
service = OrderService()

# Order endpoints
@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    """Create a new order."""
    return service.create_order(db, order)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get order by ID."""
    order = service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/", response_model=List[OrderResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    customer_id: Optional[int] = None,
    order_type: Optional[str] = None,
    order_status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List orders with optional filters."""
    return service.list_orders(
        db, skip=skip, limit=limit,
        customer_id=customer_id,
        order_type=order_type,
        order_status=order_status,
        start_date=start_date,
        end_date=end_date
    )

@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db)
):
    """Update order information."""
    updated = service.update_order(db, order_id, order)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated

@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Delete order."""
    success = service.delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"status": "success"}

# Order Detail endpoints
@router.post("/{order_id}/details", response_model=OrderDetailResponse)
def add_order_detail(
    order_id: int,
    detail: OrderDetailCreate,
    db: Session = Depends(get_db)
):
    """Add detail to order."""
    return service.add_order_detail(db, order_id, detail)

@router.get("/{order_id}/details", response_model=List[OrderDetailResponse])
def list_order_details(
    order_id: int,
    db: Session = Depends(get_db)
):
    """List order details."""
    return service.list_order_details(db, order_id)

@router.put("/details/{detail_id}", response_model=OrderDetailResponse)
def update_order_detail(
    detail_id: int,
    detail: OrderDetailUpdate,
    db: Session = Depends(get_db)
):
    """Update order detail."""
    updated = service.update_order_detail(db, detail_id, detail)
    if not updated:
        raise HTTPException(status_code=404, detail="Order detail not found")
    return updated

@router.delete("/details/{detail_id}")
def delete_order_detail(
    detail_id: int,
    db: Session = Depends(get_db)
):
    """Delete order detail."""
    success = service.delete_order_detail(db, detail_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order detail not found")
    return {"status": "success"}

# Serial Transaction endpoints
@router.post("/serials", response_model=SerialTransactionResponse)
def create_serial_transaction(
    transaction: SerialTransactionCreate,
    db: Session = Depends(get_db)
):
    """Create a new serial transaction."""
    return service.create_serial_transaction(db, transaction)

@router.get("/serials/{serial_number}", response_model=SerialTransactionResponse)
def get_serial_transaction(
    serial_number: str,
    db: Session = Depends(get_db)
):
    """Get serial transaction by serial number."""
    transaction = service.get_serial_transaction(db, serial_number)
    if not transaction:
        raise HTTPException(status_code=404, detail="Serial transaction not found")
    return transaction

@router.get("/serials", response_model=List[SerialTransactionResponse])
def list_serial_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    order_id: Optional[int] = None,
    item_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List serial transactions with optional filters."""
    return service.list_serial_transactions(
        db, skip=skip, limit=limit,
        order_id=order_id,
        item_id=item_id,
        transaction_type=transaction_type
    )

# Order Survey endpoints
@router.post("/{order_id}/survey", response_model=OrderSurveyResponse)
def create_order_survey(
    order_id: int,
    survey: OrderSurveyCreate,
    db: Session = Depends(get_db)
):
    """Create a new order survey."""
    return service.create_order_survey(db, order_id, survey)

@router.get("/{order_id}/survey", response_model=OrderSurveyResponse)
def get_order_survey(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get survey for an order."""
    survey = service.get_order_survey(db, order_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey

@router.put("/surveys/{survey_id}", response_model=OrderSurveyResponse)
def update_order_survey(
    survey_id: int,
    survey: OrderSurveyUpdate,
    db: Session = Depends(get_db)
):
    """Update order survey."""
    updated = service.update_order_survey(db, survey_id, survey)
    if not updated:
        raise HTTPException(status_code=404, detail="Survey not found")
    return updated
