"""
Doctor/Provider service layer for AriesOne SaaS application.
Implements business logic for managing healthcare providers and their credentials.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.doctor import (
    Doctor, DoctorType, ProviderNumber, ProviderNumberType
)
from ..schemas.doctor import (
    DoctorCreate, DoctorUpdate,
    ProviderNumberCreate, ProviderNumberUpdate
)

class DoctorService:
    """Service for managing doctors/healthcare providers."""

    def __init__(self, db: Session):
        self.db = db

    def get_doctor_by_id(self, doctor_id: int) -> Optional[Doctor]:
        """Retrieve a doctor by ID."""
        return self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

    def get_doctor_by_npi(self, npi: str) -> Optional[Doctor]:
        """Retrieve a doctor by NPI number."""
        return self.db.query(Doctor).filter(Doctor.npi == npi).first()

    def get_doctors(
        self,
        type_id: Optional[int] = None,
        pecos_enrolled: Optional[bool] = None,
        active_license: Optional[bool] = None
    ) -> List[Doctor]:
        """
        Get doctors with optional filtering.
        
        Args:
            type_id: Filter by doctor type
            pecos_enrolled: Filter by PECOS enrollment status
            active_license: Filter by license status
        """
        query = self.db.query(Doctor)
        
        if type_id is not None:
            query = query.filter(Doctor.type_id == type_id)
        
        if pecos_enrolled is not None:
            query = query.filter(Doctor.pecos_enrolled == pecos_enrolled)
        
        if active_license:
            query = query.filter(or_(
                Doctor.license_expired.is_(None),
                Doctor.license_expired > date.today()
            ))
            
        return query.order_by(Doctor.last_name, Doctor.first_name).all()

    def create_doctor(self, data: DoctorCreate) -> Doctor:
        """Create a new doctor record."""
        doctor = Doctor(**data.dict())
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def update_doctor(self, doctor_id: int, data: DoctorUpdate) -> Optional[Doctor]:
        """Update an existing doctor record."""
        doctor = self.get_doctor_by_id(doctor_id)
        if not doctor:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(doctor, key, value)

        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def verify_credentials(self, doctor_id: int) -> Dict[str, Any]:
        """
        Verify doctor's credentials and return status.
        
        Checks:
        - License expiration
        - PECOS enrollment
        - Required identifiers
        - Missing MIR fields
        """
        doctor = self.get_doctor_by_id(doctor_id)
        if not doctor:
            return {"error": "Doctor not found"}

        status = {
            "license_active": True,
            "license_expiration": None,
            "pecos_enrolled": doctor.pecos_enrolled,
            "missing_identifiers": [],
            "missing_mir": []
        }

        # Check license
        if doctor.license_expired:
            if doctor.license_expired < date.today():
                status["license_active"] = False
            status["license_expiration"] = doctor.license_expired

        # Check required identifiers
        required_ids = ["npi", "upin_number", "medicaid_number"]
        for id_field in required_ids:
            if not getattr(doctor, id_field):
                status["missing_identifiers"].append(id_field)

        # Check MIR fields
        required_mir = set(["FirstName", "LastName", "NPI"])
        current_mir = set(doctor.mir.split(",")) if doctor.mir else set()
        status["missing_mir"] = list(required_mir - current_mir)

        return status

class ProviderNumberService:
    """Service for managing provider identification numbers."""

    def __init__(self, db: Session):
        self.db = db

    def get_provider_number_by_id(self, number_id: int) -> Optional[ProviderNumber]:
        """Retrieve a provider number by ID."""
        return self.db.query(ProviderNumber).filter(ProviderNumber.id == number_id).first()

    def get_provider_numbers(
        self,
        doctor_id: int,
        type_id: Optional[int] = None,
        active_only: bool = True
    ) -> List[ProviderNumber]:
        """Get provider numbers for a doctor."""
        query = self.db.query(ProviderNumber).filter(ProviderNumber.doctor_id == doctor_id)
        
        if type_id is not None:
            query = query.filter(ProviderNumber.type_id == type_id)
            
        if active_only:
            query = query.filter(ProviderNumber.is_active == True)
            
        return query.all()

    def create_provider_number(self, data: ProviderNumberCreate) -> ProviderNumber:
        """Create a new provider number."""
        provider_number = ProviderNumber(**data.dict())
        self.db.add(provider_number)
        self.db.commit()
        self.db.refresh(provider_number)
        return provider_number

    def update_provider_number(
        self,
        number_id: int,
        data: ProviderNumberUpdate
    ) -> Optional[ProviderNumber]:
        """Update an existing provider number."""
        provider_number = self.get_provider_number_by_id(number_id)
        if not provider_number:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(provider_number, key, value)

        self.db.commit()
        self.db.refresh(provider_number)
        return provider_number

    def verify_provider_numbers(self, doctor_id: int) -> Dict[str, Any]:
        """
        Verify provider numbers for a doctor.
        
        Checks:
        - Missing required numbers
        - Expired numbers
        - Inactive numbers
        """
        numbers = self.get_provider_numbers(doctor_id, active_only=False)
        
        status = {
            "expired": [],
            "inactive": [],
            "missing_types": []
        }

        # Check expiration and active status
        for number in numbers:
            if number.expiration_date and number.expiration_date < date.today():
                status["expired"].append({
                    "id": number.id,
                    "type": number.number_type.name,
                    "number": number.number,
                    "expiration": number.expiration_date
                })
                
            if not number.is_active:
                status["inactive"].append({
                    "id": number.id,
                    "type": number.number_type.name,
                    "number": number.number
                })

        # Check for missing required types
        required_types = {1, 2, 3}  # Example required type IDs
        current_types = {n.type_id for n in numbers}
        status["missing_types"] = list(required_types - current_types)

        return status
