"""
Medical domain API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..models.medical import CMNForm, Doctor, Facility, ICD10Code, ICD9Code
from ..schemas.medical import (
    CMNFormCreate, CMNFormUpdate, CMNFormResponse,
    DoctorCreate, DoctorUpdate, DoctorResponse,
    FacilityCreate, FacilityUpdate, FacilityResponse,
    ICD10CodeCreate, ICD10CodeResponse,
    ICD9CodeCreate, ICD9CodeResponse
)
from ..dependencies.database import get_db
from ..services.medical import MedicalService

router = APIRouter()
service = MedicalService()

# CMN Form endpoints
@router.post("/cmn-forms", response_model=CMNFormResponse)
def create_cmn_form(
    form: CMNFormCreate,
    db: Session = Depends(get_db)
):
    """Create a new CMN form."""
    return service.create_cmn_form(db, form)

@router.get("/cmn-forms/{form_id}", response_model=CMNFormResponse)
def get_cmn_form(
    form_id: int,
    db: Session = Depends(get_db)
):
    """Get CMN form by ID."""
    form = service.get_cmn_form(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="CMN form not found")
    return form

@router.get("/cmn-forms", response_model=List[CMNFormResponse])
def list_cmn_forms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    customer_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    form_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List CMN forms with optional filters."""
    return service.list_cmn_forms(
        db, skip=skip, limit=limit,
        customer_id=customer_id,
        doctor_id=doctor_id,
        form_type=form_type
    )

@router.put("/cmn-forms/{form_id}", response_model=CMNFormResponse)
def update_cmn_form(
    form_id: int,
    form: CMNFormUpdate,
    db: Session = Depends(get_db)
):
    """Update CMN form."""
    updated = service.update_cmn_form(db, form_id, form)
    if not updated:
        raise HTTPException(status_code=404, detail="CMN form not found")
    return updated

# Doctor endpoints
@router.post("/doctors", response_model=DoctorResponse)
def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db)
):
    """Create a new doctor."""
    return service.create_doctor(db, doctor)

@router.get("/doctors/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get doctor by ID."""
    doctor = service.get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.get("/doctors", response_model=List[DoctorResponse])
def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    specialty: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List doctors with optional filters."""
    return service.list_doctors(
        db, skip=skip, limit=limit,
        search=search, specialty=specialty,
        is_active=is_active
    )

@router.put("/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor: DoctorUpdate,
    db: Session = Depends(get_db)
):
    """Update doctor information."""
    updated = service.update_doctor(db, doctor_id, doctor)
    if not updated:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return updated

# Facility endpoints
@router.post("/facilities", response_model=FacilityResponse)
def create_facility(
    facility: FacilityCreate,
    db: Session = Depends(get_db)
):
    """Create a new facility."""
    return service.create_facility(db, facility)

@router.get("/facilities/{facility_id}", response_model=FacilityResponse)
def get_facility(
    facility_id: int,
    db: Session = Depends(get_db)
):
    """Get facility by ID."""
    facility = service.get_facility(db, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility

@router.get("/facilities", response_model=List[FacilityResponse])
def list_facilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    facility_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List facilities with optional filters."""
    return service.list_facilities(
        db, skip=skip, limit=limit,
        search=search, facility_type=facility_type,
        is_active=is_active
    )

@router.put("/facilities/{facility_id}", response_model=FacilityResponse)
def update_facility(
    facility_id: int,
    facility: FacilityUpdate,
    db: Session = Depends(get_db)
):
    """Update facility information."""
    updated = service.update_facility(db, facility_id, facility)
    if not updated:
        raise HTTPException(status_code=404, detail="Facility not found")
    return updated

# ICD-10 Code endpoints
@router.get("/icd10/{code}", response_model=ICD10CodeResponse)
def get_icd10_code(
    code: str,
    db: Session = Depends(get_db)
):
    """Get ICD-10 code."""
    code = service.get_icd10_code(db, code)
    if not code:
        raise HTTPException(status_code=404, detail="ICD-10 code not found")
    return code

@router.get("/icd10", response_model=List[ICD10CodeResponse])
def list_icd10_codes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List ICD-10 codes with optional filters."""
    return service.list_icd10_codes(
        db, skip=skip, limit=limit,
        search=search, category=category
    )

# ICD-9 Code endpoints (for legacy support)
@router.get("/icd9/{code}", response_model=ICD9CodeResponse)
def get_icd9_code(
    code: str,
    db: Session = Depends(get_db)
):
    """Get ICD-9 code."""
    code = service.get_icd9_code(db, code)
    if not code:
        raise HTTPException(status_code=404, detail="ICD-9 code not found")
    return code

@router.get("/icd9", response_model=List[ICD9CodeResponse])
def list_icd9_codes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List ICD-9 codes with optional filters."""
    return service.list_icd9_codes(
        db, skip=skip, limit=limit,
        search=search, category=category
    )
