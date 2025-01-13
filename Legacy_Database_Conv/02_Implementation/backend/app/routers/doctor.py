"""
Doctor/Provider API router for AriesOne SaaS application.
Implements REST endpoints for managing healthcare providers and their credentials.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..services.doctor import DoctorService, ProviderNumberService
from ..schemas.doctor import (
    DoctorCreate, DoctorUpdate, DoctorResponse,
    DoctorTypeCreate, DoctorTypeUpdate, DoctorTypeResponse,
    ProviderNumberCreate, ProviderNumberUpdate, ProviderNumberResponse,
    ProviderNumberTypeCreate, ProviderNumberTypeUpdate, ProviderNumberTypeResponse
)
from ..dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/v1/doctors",
    tags=["doctors"]
)

# Doctor Type Routes

@router.get("/types", response_model=List[DoctorTypeResponse])
async def list_doctor_types(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all doctor types."""
    service = DoctorService(db)
    return service.get_doctor_types()

@router.post("/types", response_model=DoctorTypeResponse)
async def create_doctor_type(
    type_data: DoctorTypeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new doctor type."""
    service = DoctorService(db)
    type_data.created_by_id = current_user.id
    type_data.last_update_user_id = current_user.id
    return service.create_doctor_type(type_data)

@router.put("/types/{type_id}", response_model=DoctorTypeResponse)
async def update_doctor_type(
    type_id: int,
    type_data: DoctorTypeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing doctor type."""
    service = DoctorService(db)
    type_data.last_update_user_id = current_user.id
    doctor_type = service.update_doctor_type(type_id, type_data)
    if not doctor_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor type not found"
        )
    return doctor_type

# Doctor Routes

@router.get("", response_model=List[DoctorResponse])
async def list_doctors(
    type_id: Optional[int] = None,
    pecos_enrolled: Optional[bool] = None,
    active_license: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List doctors with optional filtering."""
    service = DoctorService(db)
    return service.get_doctors(
        type_id=type_id,
        pecos_enrolled=pecos_enrolled,
        active_license=active_license
    )

@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific doctor by ID."""
    service = DoctorService(db)
    doctor = service.get_doctor_by_id(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    return doctor

@router.post("", response_model=DoctorResponse)
async def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new doctor."""
    service = DoctorService(db)
    doctor_data.created_by_id = current_user.id
    doctor_data.last_update_user_id = current_user.id
    return service.create_doctor(doctor_data)

@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing doctor."""
    service = DoctorService(db)
    doctor_data.last_update_user_id = current_user.id
    doctor = service.update_doctor(doctor_id, doctor_data)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    return doctor

@router.get("/{doctor_id}/verify", response_model=dict)
async def verify_doctor_credentials(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Verify a doctor's credentials."""
    service = DoctorService(db)
    result = service.verify_credentials(doctor_id)
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    return result

# Provider Number Routes

@router.get("/{doctor_id}/numbers", response_model=List[ProviderNumberResponse])
async def list_provider_numbers(
    doctor_id: int,
    type_id: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List provider numbers for a doctor."""
    service = ProviderNumberService(db)
    return service.get_provider_numbers(
        doctor_id=doctor_id,
        type_id=type_id,
        active_only=active_only
    )

@router.post("/numbers", response_model=ProviderNumberResponse)
async def create_provider_number(
    number_data: ProviderNumberCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new provider number."""
    service = ProviderNumberService(db)
    number_data.created_by_id = current_user.id
    number_data.last_update_user_id = current_user.id
    return service.create_provider_number(number_data)

@router.put("/numbers/{number_id}", response_model=ProviderNumberResponse)
async def update_provider_number(
    number_id: int,
    number_data: ProviderNumberUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing provider number."""
    service = ProviderNumberService(db)
    number_data.last_update_user_id = current_user.id
    provider_number = service.update_provider_number(number_id, number_data)
    if not provider_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider number not found"
        )
    return provider_number

@router.get("/{doctor_id}/numbers/verify", response_model=dict)
async def verify_provider_numbers(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Verify provider numbers for a doctor."""
    service = ProviderNumberService(db)
    return service.verify_provider_numbers(doctor_id)
