"""
Doctor/Provider models for AriesOne SaaS application.
Implements data models for managing healthcare providers and their credentials.
"""
from datetime import datetime, date
from typing import Optional, List, Set
from sqlalchemy import Column, Integer, String, Date, Boolean, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import SET

from ..database import Base
from ..models.common import AuditMixin

class DoctorType(Base, AuditMixin):
    """Doctor/Provider type classification."""
    __tablename__ = "tbl_doctortype"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    # Relationships
    doctors = relationship("Doctor", back_populates="doctor_type")

class Doctor(Base, AuditMixin):
    """Doctor/Healthcare provider model."""
    __tablename__ = "tbl_doctor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey("tbl_doctortype.id"), nullable=True)
    
    # Name fields
    courtesy = Column(Enum("Dr.", "Miss", "Mr.", "Mrs.", "Rev."), nullable=False)
    first_name = Column(String(25), nullable=False)
    middle_name = Column(String(1), nullable=False)
    last_name = Column(String(30), nullable=False)
    suffix = Column(String(4), nullable=False)
    title = Column(String(50), nullable=False)
    
    # Contact information
    address1 = Column(String(40), nullable=False)
    address2 = Column(String(40), nullable=False)
    city = Column(String(25), nullable=False)
    state = Column(String(2), nullable=False)
    zip = Column(String(10), nullable=False)
    phone = Column(String(50), nullable=False)
    phone2 = Column(String(50), nullable=False)
    fax = Column(String(50), nullable=False)
    contact = Column(String(50), nullable=False)
    
    # Identifiers and credentials
    npi = Column(String(10), nullable=True)
    upin_number = Column(String(11), nullable=False)
    license_number = Column(String(16), nullable=False)
    license_expired = Column(Date, nullable=True)
    medicaid_number = Column(String(16), nullable=False)
    fed_tax_id = Column(String(9), nullable=False)
    dea_number = Column(String(20), nullable=False)
    other_id = Column(String(16), nullable=False)
    pecos_enrolled = Column(Boolean, nullable=False, default=False)
    
    # Required Information fields
    mir = Column(SET("FirstName", "LastName", "Address1", "City", "State", "Zip", "NPI", "Phone"), 
                nullable=False, default="")

    # Relationships
    doctor_type = relationship("DoctorType", back_populates="doctors")
    cmn_forms = relationship("CMNForm", back_populates="doctor")
    orders = relationship("Order", back_populates="doctor")

class ProviderNumberType(Base, AuditMixin):
    """Provider number type classification."""
    __tablename__ = "tbl_providernumbertype"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)

    # Relationships
    provider_numbers = relationship("ProviderNumber", back_populates="number_type")

class ProviderNumber(Base, AuditMixin):
    """Provider identification numbers."""
    __tablename__ = "tbl_provider"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("tbl_doctor.id"), nullable=False)
    type_id = Column(Integer, ForeignKey("tbl_providernumbertype.id"), nullable=False)
    number = Column(String(50), nullable=False)
    expiration_date = Column(Date, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    notes = Column(String(255), nullable=True)

    # Relationships
    doctor = relationship("Doctor", backref="provider_numbers")
    number_type = relationship("ProviderNumberType", back_populates="provider_numbers")
