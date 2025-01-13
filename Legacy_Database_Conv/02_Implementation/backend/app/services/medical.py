"""
Medical domain business logic and database operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.medical import (
    CMNForm, Doctor, Facility, DoctorFacility,
    ICD10Code, ICD9Code
)
from ..schemas.medical import (
    CMNFormCreate, CMNFormUpdate,
    DoctorCreate, DoctorUpdate,
    FacilityCreate, FacilityUpdate,
    ICD10CodeCreate, ICD9CodeCreate
)

class MedicalService:
    def create_cmn_form(self, db: Session, form: CMNFormCreate) -> CMNForm:
        """Create a new CMN form."""
        db_form = CMNForm(**form.dict())
        db.add(db_form)
        db.commit()
        db.refresh(db_form)
        return db_form

    def get_cmn_form(self, db: Session, form_id: int) -> Optional[CMNForm]:
        """Get CMN form by ID."""
        return db.query(CMNForm).filter(CMNForm.id == form_id).first()

    def list_cmn_forms(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        form_type: Optional[str] = None
    ) -> List[CMNForm]:
        """List CMN forms with optional filters."""
        query = db.query(CMNForm)
        
        if customer_id:
            query = query.filter(CMNForm.customer_id == customer_id)
        if doctor_id:
            query = query.filter(CMNForm.doctor_id == doctor_id)
        if form_type:
            query = query.filter(CMNForm.form_type == form_type)
            
        return query.offset(skip).limit(limit).all()

    def update_cmn_form(
        self,
        db: Session,
        form_id: int,
        form: CMNFormUpdate
    ) -> Optional[CMNForm]:
        """Update CMN form."""
        db_form = self.get_cmn_form(db, form_id)
        if not db_form:
            return None
            
        for key, value in form.dict(exclude_unset=True).items():
            setattr(db_form, key, value)
            
        db.add(db_form)
        db.commit()
        db.refresh(db_form)
        return db_form

    def create_doctor(self, db: Session, doctor: DoctorCreate) -> Doctor:
        """Create a new doctor."""
        db_doctor = Doctor(**doctor.dict())
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor

    def get_doctor(self, db: Session, doctor_id: int) -> Optional[Doctor]:
        """Get doctor by ID."""
        return db.query(Doctor).filter(Doctor.id == doctor_id).first()

    def list_doctors(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        specialty: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Doctor]:
        """List doctors with optional filters."""
        query = db.query(Doctor)
        
        if search:
            search_filter = or_(
                Doctor.first_name.ilike(f"%{search}%"),
                Doctor.last_name.ilike(f"%{search}%"),
                Doctor.npi.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
            
        if specialty:
            query = query.filter(Doctor.specialty == specialty)
        if is_active is not None:
            query = query.filter(Doctor.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()

    def update_doctor(
        self,
        db: Session,
        doctor_id: int,
        doctor: DoctorUpdate
    ) -> Optional[Doctor]:
        """Update doctor information."""
        db_doctor = self.get_doctor(db, doctor_id)
        if not db_doctor:
            return None
            
        for key, value in doctor.dict(exclude_unset=True).items():
            setattr(db_doctor, key, value)
            
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor

    def create_facility(self, db: Session, facility: FacilityCreate) -> Facility:
        """Create a new facility."""
        db_facility = Facility(**facility.dict())
        db.add(db_facility)
        db.commit()
        db.refresh(db_facility)
        return db_facility

    def get_facility(self, db: Session, facility_id: int) -> Optional[Facility]:
        """Get facility by ID."""
        return db.query(Facility).filter(Facility.id == facility_id).first()

    def list_facilities(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        facility_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Facility]:
        """List facilities with optional filters."""
        query = db.query(Facility)
        
        if search:
            search_filter = or_(
                Facility.name.ilike(f"%{search}%"),
                Facility.facility_code.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
            
        if facility_type:
            query = query.filter(Facility.type == facility_type)
        if is_active is not None:
            query = query.filter(Facility.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()

    def update_facility(
        self,
        db: Session,
        facility_id: int,
        facility: FacilityUpdate
    ) -> Optional[Facility]:
        """Update facility information."""
        db_facility = self.get_facility(db, facility_id)
        if not db_facility:
            return None
            
        for key, value in facility.dict(exclude_unset=True).items():
            setattr(db_facility, key, value)
            
        db.add(db_facility)
        db.commit()
        db.refresh(db_facility)
        return db_facility

    def get_icd10_code(self, db: Session, code: str) -> Optional[ICD10Code]:
        """Get ICD-10 code."""
        return db.query(ICD10Code).filter(ICD10Code.code == code).first()

    def list_icd10_codes(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ICD10Code]:
        """List ICD-10 codes with optional filters."""
        query = db.query(ICD10Code)
        
        if search:
            search_filter = or_(
                ICD10Code.code.ilike(f"%{search}%"),
                ICD10Code.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
            
        if category:
            query = query.filter(ICD10Code.category == category)
            
        return query.offset(skip).limit(limit).all()

    def get_icd9_code(self, db: Session, code: str) -> Optional[ICD9Code]:
        """Get ICD-9 code."""
        return db.query(ICD9Code).filter(ICD9Code.code == code).first()

    def list_icd9_codes(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ICD9Code]:
        """List ICD-9 codes with optional filters."""
        query = db.query(ICD9Code)
        
        if search:
            search_filter = or_(
                ICD9Code.code.ilike(f"%{search}%"),
                ICD9Code.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
            
        if category:
            query = query.filter(ICD9Code.category == category)
            
        return query.offset(skip).limit(limit).all()
