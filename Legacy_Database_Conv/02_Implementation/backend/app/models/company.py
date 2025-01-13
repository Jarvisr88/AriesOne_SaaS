"""
Company domain models for AriesOne SaaS application.
This module implements the core company functionality including
organizations, locations, departments, and employees.
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.sql import func

from .base import Base

class OrganizationStatus(str, Enum):
    """Organization status types."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    PENDING = "Pending"

class EmployeeStatus(str, Enum):
    """Employee status types."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ON_LEAVE = "OnLeave"
    TERMINATED = "Terminated"

class BaseOrganizationalUnit(Base):
    """
    Abstract base class for organizational units.
    Provides common attributes and methods for all unit types.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    status = Column(SQLEnum(OrganizationStatus), nullable=False, default=OrganizationStatus.ACTIVE)
    
    # Contact Information
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(200))
    
    # Dates
    effective_start_date = Column(Date, nullable=False, default=func.current_date())
    effective_end_date = Column(Date)
    
    # Notes
    description = Column(String(500))
    internal_notes = Column(String(500))
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Common relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

class Company(BaseOrganizationalUnit):
    """
    Company model representing the top-level organization.
    """
    __tablename__ = 'companies'

    # Business Information
    tax_id = Column(String(20))
    dme_license_number = Column(String(50))
    npi_number = Column(String(10))
    
    # Address
    address_line1 = Column(String(100), nullable=False)
    address_line2 = Column(String(100))
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    country = Column(String(2), nullable=False, default='US')
    
    # Settings
    fiscal_year_start = Column(Integer, nullable=False, default=1)  # Month (1-12)
    time_zone = Column(String(50), nullable=False, default='America/Chicago')
    currency = Column(String(3), nullable=False, default='USD')
    
    # Relationships
    locations = relationship("Location", back_populates="company")
    departments = relationship("Department", back_populates="company")
    employees = relationship("Employee", back_populates="company")

    def __repr__(self):
        return f"<Company {self.name}>"

class Location(BaseOrganizationalUnit):
    """
    Location model representing physical business locations.
    """
    __tablename__ = 'locations'

    # References
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    
    # Address
    address_line1 = Column(String(100), nullable=False)
    address_line2 = Column(String(100))
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    country = Column(String(2), nullable=False, default='US')
    
    # Operating Information
    is_warehouse = Column(Boolean, default=False)
    is_service_center = Column(Boolean, default=False)
    service_radius = Column(Integer)  # In miles
    operating_hours = Column(String(500))  # JSON string of operating hours
    
    # License Information
    local_license_number = Column(String(50))
    license_expiry_date = Column(Date)
    
    # Relationships
    company = relationship("Company", back_populates="locations")
    departments = relationship("Department", back_populates="location")
    employees = relationship("Employee", back_populates="location")

    def __repr__(self):
        return f"<Location {self.name} ({self.company.name})>"

class Department(BaseOrganizationalUnit):
    """
    Department model representing internal organizational units.
    """
    __tablename__ = 'departments'

    # References
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'))
    parent_department_id = Column(Integer, ForeignKey('departments.id'))
    
    # Department Information
    department_type = Column(String(50))
    cost_center = Column(String(20))
    budget_code = Column(String(20))
    
    # Relationships
    company = relationship("Company", back_populates="departments")
    location = relationship("Location", back_populates="departments")
    parent_department = relationship("Department", remote_side=[id])
    child_departments = relationship("Department")
    employees = relationship("Employee", back_populates="department")

    def __repr__(self):
        return f"<Department {self.name} ({self.company.name})>"

# Employee-Role association table
employee_roles = Table(
    'employee_roles',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class Employee(Base):
    """
    Employee model representing company staff members.
    """
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_number = Column(String(20), unique=True, nullable=False)
    
    # References
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Personal Information
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20))
    
    # Employment Information
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    status = Column(SQLEnum(EmployeeStatus), nullable=False, default=EmployeeStatus.ACTIVE)
    is_full_time = Column(Boolean, default=True)
    
    # Professional Information
    title = Column(String(100))
    license_number = Column(String(50))
    license_expiry_date = Column(Date)
    certifications = Column(String(500))  # JSON string of certifications
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="employees")
    location = relationship("Location", back_populates="employees")
    department = relationship("Department", back_populates="employees")
    user = relationship("User", foreign_keys=[user_id])
    roles = relationship("Role", secondary=employee_roles)
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<Employee {self.first_name} {self.last_name}>"

class Role(Base):
    """
    Role model for employee role assignments.
    """
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(String(200))
    
    # Role Information
    is_system_role = Column(Boolean, default=False)
    permissions = Column(String(1000))  # JSON string of permissions
    
    # System Fields
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, default=func.now())
    last_update_user_id = Column(Integer, ForeignKey('users.id'))
    last_update_datetime = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    employees = relationship("Employee", secondary=employee_roles)
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_update_user = relationship("User", foreign_keys=[last_update_user_id])

    def __repr__(self):
        return f"<Role {self.name}>"
