"""
Medical domain models for AriesOne SaaS application.
This module contains SQLAlchemy models for medical-related entities including
CMN forms, doctors, facilities, and medical codes.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class CMNFormType(str, Enum):
    """CMN form types supported by the system."""
    DMERC_0102A = "DMERC 01.02A"
    DMERC_0102B = "DMERC 01.02B"
    DMERC_0203A = "DMERC 02.03A"
    DMERC_0203B = "DMERC 02.03B"
    DMERC_0302 = "DMERC 03.02"
    DMERC_0403B = "DMERC 04.03B"
    DMERC_0403C = "DMERC 04.03C"
    DMERC_0602B = "DMERC 06.02B"
    DMERC_0702A = "DMERC 07.02A"
    DMERC_0702B = "DMERC 07.02B"
    DMERC_0802 = "DMERC 08.02"
    DMERC_0902 = "DMERC 09.02"
    DMERC_1002A = "DMERC 10.02A"
    DMERC_1002B = "DMERC 10.02B"
    DMERC_4842 = "DMERC 484.2"
    DMERC_DRORDER = "DMERC DRORDER"
    DMERC_URO = "DMERC URO"
    DME_0404B = "DME 04.04B"
    DME_0404C = "DME 04.04C"
    DME_0603B = "DME 06.03B"
    DME_0703A = "DME 07.03A"
    DME_0903 = "DME 09.03"
    DME_1003 = "DME 10.03"
    DME_48403 = "DME 484.03"

class CMNForm(Base):
    """
    Certificate of Medical Necessity (CMN) form.
    Maps to the modernized version of tbl_cmnform.
    """
    __tablename__ = 'cmn_forms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    form_type = Column(SQLEnum(CMNFormType), nullable=False)
    
    # Dates
    initial_date = Column(Date)
    revised_date = Column(Date)
    recertification_date = Column(Date)
    
    # Form Details
    pos_type_id = Column(Integer, ForeignKey('pos_types.id'))
    answering_name = Column(String(50))
    signature_name = Column(String(50))
    signature_date = Column(Date)
    
    # Status
    status = Column(String(20), nullable=False, default='Draft')
    is_active = Column(Boolean, nullable=False, default=True)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="cmn_forms")
    doctor = relationship("Doctor", back_populates="cmn_forms")
    pos_type = relationship("POSType")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<CMNForm {self.id}: {self.form_type} - {self.customer_id}>"

class Doctor(Base):
    """
    Doctor/Physician information.
    Maps to the modernized version of doctor table.
    """
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    npi = Column(String(10), unique=True)
    upin = Column(String(20))
    license_number = Column(String(20))
    
    # Personal Information
    first_name = Column(String(25), nullable=False)
    middle_name = Column(String(1))
    last_name = Column(String(30), nullable=False)
    suffix = Column(String(4))
    credentials = Column(String(20))
    specialty = Column(String(50))
    
    # Contact Information
    address1 = Column(String(40), nullable=False)
    address2 = Column(String(40))
    city = Column(String(25), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    phone = Column(String(50), nullable=False)
    fax = Column(String(50))
    email = Column(String(100))
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    inactive_date = Column(Date)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    cmn_forms = relationship("CMNForm", back_populates="doctor")
    facilities = relationship("DoctorFacility", back_populates="doctor")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<Doctor {self.id}: {self.first_name} {self.last_name}>"

class Facility(Base):
    """
    Medical facility information.
    Maps to the modernized version of facility table.
    """
    __tablename__ = 'facilities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    facility_code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50))
    
    # Contact Information
    address1 = Column(String(40), nullable=False)
    address2 = Column(String(40))
    city = Column(String(25), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    phone = Column(String(50), nullable=False)
    fax = Column(String(50))
    email = Column(String(100))
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    inactive_date = Column(Date)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    doctors = relationship("DoctorFacility", back_populates="facility")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<Facility {self.id}: {self.name}>"

class DoctorFacility(Base):
    """
    Association between doctors and facilities.
    """
    __tablename__ = 'doctor_facilities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    facility_id = Column(Integer, ForeignKey('facilities.id'), nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)
    start_date = Column(Date)
    end_date = Column(Date)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    doctor = relationship("Doctor", back_populates="facilities")
    facility = relationship("Facility", back_populates="doctors")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<DoctorFacility {self.doctor_id} - {self.facility_id}>"

class ICD10Code(Base):
    """
    ICD-10 diagnosis codes.
    Maps to the modernized version of icd10 table.
    """
    __tablename__ = 'icd10_codes'

    code = Column(String(8), primary_key=True)
    description = Column(String(255), nullable=False)
    category = Column(String(50))
    is_active = Column(Boolean, nullable=False, default=True)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<ICD10Code {self.code}: {self.description}>"

class ICD9Code(Base):
    """
    ICD-9 diagnosis codes (for legacy support).
    Maps to the modernized version of icd9 table.
    """
    __tablename__ = 'icd9_codes'

    code = Column(String(6), primary_key=True)
    description = Column(String(255), nullable=False)
    category = Column(String(50))
    icd10_mapping = Column(String(8), ForeignKey('icd10_codes.code'))
    is_active = Column(Boolean, nullable=False, default=True)
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    icd10_code = relationship("ICD10Code")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<ICD9Code {self.code}: {self.description}>"
