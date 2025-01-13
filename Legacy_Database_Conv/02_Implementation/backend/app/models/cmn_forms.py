"""
CMN Forms domain models for AriesOne SaaS application.
This module implements Certificate of Medical Necessity (CMN) forms
and their type-specific variations.
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Enum as SQLEnum
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

class CMNStatus(str, Enum):
    """CMN form status types."""
    DRAFT = "Draft"
    PENDING = "Pending"
    SIGNED = "Signed"
    EXPIRED = "Expired"
    REVISED = "Revised"
    VOID = "Void"

class AnswerType(str, Enum):
    """Standard answer types for CMN questions."""
    YES = "Y"
    NO = "N"
    DEFAULT = "D"

class BaseCMNForm(Base):
    """
    Base class for all CMN forms.
    Provides common attributes and functionality.
    """
    __tablename__ = 'cmn_forms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    form_type = Column(SQLEnum(CMNFormType), nullable=False)
    form_status = Column(SQLEnum(CMNStatus), nullable=False, default=CMNStatus.DRAFT)
    
    # Relationships
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    
    # Dates
    initial_date = Column(Date)
    revised_date = Column(Date)
    expiration_date = Column(Date)
    signed_date = Column(Date)
    
    # Diagnosis Codes
    icd10_codes = Column(String(500))  # Comma-separated list of ICD-10 codes
    
    # Tracking
    is_active = Column(Boolean, nullable=False, default=True)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="cmn_forms")
    doctor = relationship("Doctor", back_populates="cmn_forms")
    order = relationship("Order", back_populates="cmn_forms")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    __mapper_args__ = {
        'polymorphic_identity': 'base_cmn',
        'polymorphic_on': form_type
    }

class CMNForm0102A(BaseCMNForm):
    """DMERC 01.02A - Oxygen form."""
    __tablename__ = 'cmn_form_0102a'

    id = Column(Integer, ForeignKey('cmn_forms.id'), primary_key=True)
    answer1 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer2 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer3 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer4 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer5 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    test_condition = Column(String(50))
    test_date = Column(Date)
    o2_saturation = Column(Integer)
    arterial_po2 = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': CMNFormType.DMERC_0102A
    }

class CMNForm0102B(BaseCMNForm):
    """DMERC 01.02B - Oxygen form recertification."""
    __tablename__ = 'cmn_form_0102b'

    id = Column(Integer, ForeignKey('cmn_forms.id'), primary_key=True)
    answer1 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer2 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer3 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer4 = Column(Date)
    answer5 = Column(String(100))

    __mapper_args__ = {
        'polymorphic_identity': CMNFormType.DMERC_0102B
    }

# Additional form type classes following the same pattern...
# Each form type has its specific fields and validation rules

class CMNForm48403(BaseCMNForm):
    """DME 484.03 - Updated version of the oxygen CMN."""
    __tablename__ = 'cmn_form_48403'

    id = Column(Integer, ForeignKey('cmn_forms.id'), primary_key=True)
    answer1a = Column(Integer)
    answer1b = Column(Integer)
    answer1c = Column(Date)
    answer2a = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer2b = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer3 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer4 = Column(SQLEnum(AnswerType), nullable=False, default=AnswerType.DEFAULT)
    answer5 = Column(String(100))

    __mapper_args__ = {
        'polymorphic_identity': CMNFormType.DME_48403
    }

class CMNFormDROrder(BaseCMNForm):
    """DMERC DRORDER - Doctor's order form."""
    __tablename__ = 'cmn_form_drorder'

    id = Column(Integer, ForeignKey('cmn_forms.id'), primary_key=True)
    order_details = Column(String(1000))
    prescription = Column(String(500))
    special_instructions = Column(String(500))

    __mapper_args__ = {
        'polymorphic_identity': CMNFormType.DMERC_DRORDER
    }

# Add form-specific validation methods and business logic here
