"""
Customer domain models for AriesOne SaaS application.
This module contains SQLAlchemy models for the customer domain, including customer details,
insurance information, and related entities.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class CourtesyType(str, Enum):
    DR = 'Dr.'
    MISS = 'Miss'
    MR = 'Mr.'
    MRS = 'Mrs.'
    REV = 'Rev.'

class EmploymentStatus(str, Enum):
    UNKNOWN = 'Unknown'
    FULL_TIME = 'Full Time'
    PART_TIME = 'Part Time'
    RETIRED = 'Retired'
    STUDENT = 'Student'
    UNEMPLOYED = 'Unemployed'

class MaritalStatus(str, Enum):
    UNKNOWN = 'Unknown'
    SINGLE = 'Single'
    MARRIED = 'Married'
    LEGALLY_SEPARATED = 'Legally Separated'
    DIVORCED = 'Divorced'
    WIDOWED = 'Widowed'

class MilitaryStatus(str, Enum):
    NA = 'N/A'
    ACTIVE = 'Active'
    RESERVE = 'Reserve'
    RETIRED = 'Retired'

class StudentStatus(str, Enum):
    NA = 'N/A'
    FULL_TIME = 'Full Time'
    PART_TIME = 'Part Time'

class AccidentType(str, Enum):
    AUTO = 'Auto'
    NO = 'No'
    OTHER = 'Other'

class Customer(Base):
    """
    Customer model representing the main customer/patient entity.
    Maps to the modernized version of tbl_customer.
    """
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_number = Column(String(40), nullable=False, unique=True)
    
    # Personal Information
    first_name = Column(String(25), nullable=False)
    middle_name = Column(String(1))
    last_name = Column(String(30), nullable=False)
    suffix = Column(String(4))
    courtesy = Column(SQLEnum(CourtesyType), nullable=False, default=CourtesyType.DR)
    date_of_birth = Column(Date)
    deceased_date = Column(Date)
    gender = Column(String(10))
    
    # Contact Information
    address1 = Column(String(40), nullable=False)
    address2 = Column(String(40))
    city = Column(String(25), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    phone = Column(String(50), nullable=False)
    phone2 = Column(String(50))
    delivery_directions = Column(String)
    
    # Status Information
    employment_status = Column(SQLEnum(EmploymentStatus), nullable=False, default=EmploymentStatus.UNKNOWN)
    marital_status = Column(SQLEnum(MaritalStatus), nullable=False, default=MaritalStatus.UNKNOWN)
    military_status = Column(SQLEnum(MilitaryStatus), nullable=False, default=MilitaryStatus.NA)
    student_status = Column(SQLEnum(StudentStatus), nullable=False, default=StudentStatus.NA)
    
    # Billing Information
    customer_balance = Column(Float)
    total_balance = Column(Float)
    billing_type_id = Column(Integer, ForeignKey('billing_types.id'))
    customer_class_code = Column(String(2), ForeignKey('customer_classes.code'))
    customer_type_id = Column(Integer, ForeignKey('customer_types.id'))
    
    # Billing Address
    bill_active = Column(Boolean, nullable=False, default=False)
    bill_name = Column(String(50))
    bill_address1 = Column(String(40))
    bill_address2 = Column(String(40))
    bill_city = Column(String(25))
    bill_state = Column(String(2))
    bill_zip = Column(String(10))
    
    # Shipping Information
    ship_active = Column(Boolean, nullable=False, default=False)
    ship_name = Column(String(50))
    ship_address1 = Column(String(40))
    ship_address2 = Column(String(40))
    ship_city = Column(String(25))
    ship_state = Column(String(2))
    ship_zip = Column(String(10))
    
    # Medical Information
    accident_type = Column(SQLEnum(AccidentType))
    date_of_injury = Column(Date)
    first_consult_date = Column(Date)
    return_to_work_date = Column(Date)
    pos_type_id = Column(Integer, ForeignKey('pos_types.id'))
    
    # Commercial Account
    commercial_account = Column(Boolean)
    
    # System Fields
    setup_date = Column(Date)
    inactive_date = Column(Date)
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    billing_type = relationship("BillingType", back_populates="customers")
    customer_class = relationship("CustomerClass", back_populates="customers")
    customer_type = relationship("CustomerType", back_populates="customers")
    pos_type = relationship("POSType", back_populates="customers")
    last_update_user = relationship("User", back_populates="updated_customers")
    
    insurance_policies = relationship("CustomerInsurance", back_populates="customer")
    notes = relationship("CustomerNote", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer {self.id}: {self.first_name} {self.last_name}>"

class CustomerInsurance(Base):
    """
    Customer insurance policy information.
    Maps to the modernized version of customer_insurance.
    """
    __tablename__ = 'customer_insurances'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    insurance_id = Column(Integer, ForeignKey('insurance_companies.id'), nullable=False)
    policy_number = Column(String(50), nullable=False)
    group_number = Column(String(50))
    priority = Column(Integer, nullable=False)
    effective_date = Column(Date)
    termination_date = Column(Date)
    verification_date = Column(Date)
    copay_amount = Column(Float)
    copay_percent = Column(Float)
    
    # System Fields
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="insurance_policies")
    insurance_company = relationship("InsuranceCompany", back_populates="customer_policies")
    last_update_user = relationship("User", back_populates="updated_insurance_policies")

    def __repr__(self):
        return f"<CustomerInsurance {self.id}: {self.customer_id} - {self.insurance_id}>"

class CustomerNote(Base):
    """
    Customer notes and comments.
    Maps to the modernized version of customer_notes.
    """
    __tablename__ = 'customer_notes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    note_type_id = Column(Integer, ForeignKey('note_types.id'), nullable=False)
    note_text = Column(String, nullable=False)
    note_date = Column(DateTime, nullable=False, default=func.now())
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="notes")
    note_type = relationship("NoteType")
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<CustomerNote {self.id}: {self.customer_id} - {self.note_type_id}>"
