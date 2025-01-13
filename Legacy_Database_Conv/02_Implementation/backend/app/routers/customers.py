"""
Customer domain API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..models.customer import Customer, CustomerInsurance, CustomerNote
from ..schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerInsuranceCreate, CustomerInsuranceUpdate, CustomerInsuranceResponse,
    CustomerNoteCreate, CustomerNoteResponse
)
from ..dependencies.database import get_db
from ..services.customer import CustomerService

router = APIRouter()
service = CustomerService()

@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """Create a new customer."""
    return service.create_customer(db, customer)

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Get customer by ID."""
    customer = service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List customers with optional search and pagination."""
    return service.list_customers(db, skip=skip, limit=limit, search=search)

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """Update customer information."""
    updated = service.update_customer(db, customer_id, customer)
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated

@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Delete customer."""
    success = service.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"status": "success"}

# Insurance endpoints
@router.post("/{customer_id}/insurance", response_model=CustomerInsuranceResponse)
def add_insurance(
    customer_id: int,
    insurance: CustomerInsuranceCreate,
    db: Session = Depends(get_db)
):
    """Add insurance policy to customer."""
    return service.add_insurance(db, customer_id, insurance)

@router.get("/{customer_id}/insurance", response_model=List[CustomerInsuranceResponse])
def list_insurance(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """List customer's insurance policies."""
    return service.list_insurance(db, customer_id)

# Notes endpoints
@router.post("/{customer_id}/notes", response_model=CustomerNoteResponse)
def add_note(
    customer_id: int,
    note: CustomerNoteCreate,
    db: Session = Depends(get_db)
):
    """Add note to customer."""
    return service.add_note(db, customer_id, note)

@router.get("/{customer_id}/notes", response_model=List[CustomerNoteResponse])
def list_notes(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """List customer's notes."""
    return service.list_notes(db, customer_id)
