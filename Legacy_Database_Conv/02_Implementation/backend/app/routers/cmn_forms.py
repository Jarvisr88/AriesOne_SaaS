"""
CMN Forms API router for AriesOne SaaS application.
Implements REST endpoints for Certificate of Medical Necessity (CMN) forms.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..services.cmn_forms import CMNFormService
from ..models.cmn_forms import CMNFormType, CMNStatus
from ..schemas.cmn_forms import (
    CMNFormBase, CMNFormCreate, CMNFormUpdate,
    CMNForm0102ACreate, CMNForm0102BCreate,
    CMNForm48403Create, CMNFormDROrderCreate,
    CMNFormResponse
)
from ..dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/v1/cmn-forms",
    tags=["cmn-forms"]
)

@router.get("/", response_model=List[CMNFormResponse])
async def list_forms(
    customer_id: Optional[int] = None,
    order_id: Optional[int] = None,
    form_type: Optional[CMNFormType] = None,
    status: Optional[CMNStatus] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List CMN forms with optional filtering."""
    service = CMNFormService(db)
    
    if customer_id:
        forms = service.get_forms_by_customer(customer_id)
    elif order_id:
        forms = service.get_forms_by_order(order_id)
    elif form_type:
        forms = service.get_active_forms_by_type(form_type)
    else:
        forms = service.get_active_forms_by_type(None)
    
    if status:
        forms = [f for f in forms if f.form_status == status]
    
    return forms

@router.get("/{form_id}", response_model=CMNFormResponse)
async def get_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific CMN form by ID."""
    service = CMNFormService(db)
    form = service.get_form_by_id(form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    return form

@router.post("/", response_model=CMNFormResponse)
async def create_form(
    form_data: CMNFormCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new CMN form."""
    service = CMNFormService(db)
    
    # Add audit fields
    form_data.created_by_id = current_user.id
    form_data.last_update_user_id = current_user.id
    
    try:
        form = service.create_form(form_data.form_type, form_data.dict())
        return form
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{form_id}", response_model=CMNFormResponse)
async def update_form(
    form_id: int,
    form_data: CMNFormUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing CMN form."""
    service = CMNFormService(db)
    
    # Add audit fields
    form_data.last_update_user_id = current_user.id
    
    form = service.update_form(form_id, form_data.dict(exclude_unset=True))
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    return form

@router.post("/{form_id}/sign")
async def sign_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Sign a CMN form."""
    service = CMNFormService(db)
    form = service.sign_form(form_id, current_user.id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    return form

@router.post("/{form_id}/void")
async def void_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Void a CMN form."""
    service = CMNFormService(db)
    form = service.void_form(form_id, current_user.id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    return form

@router.post("/{form_id}/revise", response_model=CMNFormResponse)
async def revise_form(
    form_id: int,
    form_data: CMNFormCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a revised version of an existing form."""
    service = CMNFormService(db)
    
    # Add audit fields
    form_data.created_by_id = current_user.id
    form_data.last_update_user_id = current_user.id
    
    form = service.revise_form(form_id, form_data.dict())
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )
    return form

@router.get("/{form_id}/validate")
async def validate_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Validate a CMN form's data."""
    service = CMNFormService(db)
    errors = service.validate_form(form_id)
    return {"errors": errors}
