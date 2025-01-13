"""
Service layer for company domain operations.
Implements business logic for companies, locations, departments, and employees.
"""
from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException

from ..models.company import (
    Company, Location, Department, Employee, Role,
    OrganizationStatus, EmployeeStatus
)
from ..schemas.company import (
    CompanyCreate, CompanyUpdate,
    LocationCreate, LocationUpdate,
    DepartmentCreate, DepartmentUpdate,
    EmployeeCreate, EmployeeUpdate,
    RoleCreate, RoleUpdate
)

class CompanyService:
    """Service for company operations."""

    @staticmethod
    async def create_company(db: Session, company: CompanyCreate, user_id: int) -> Company:
        """Create a new company."""
        db_company = Company(**company.model_dump(), created_by_id=user_id)
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company

    @staticmethod
    async def get_company(db: Session, company_id: int) -> Company:
        """Get a company by ID."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company

    @staticmethod
    async def update_company(
        db: Session, company_id: int, company: CompanyUpdate, user_id: int
    ) -> Company:
        """Update a company."""
        db_company = await CompanyService.get_company(db, company_id)
        update_data = company.model_dump(exclude_unset=True)
        update_data["last_update_user_id"] = user_id
        
        for field, value in update_data.items():
            setattr(db_company, field, value)
        
        db.commit()
        db.refresh(db_company)
        return db_company

    @staticmethod
    async def list_companies(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrganizationStatus] = None
    ) -> List[Company]:
        """List companies with optional filtering."""
        query = db.query(Company)
        if status:
            query = query.filter(Company.status == status)
        return query.offset(skip).limit(limit).all()

class LocationService:
    """Service for location operations."""

    @staticmethod
    async def create_location(db: Session, location: LocationCreate, user_id: int) -> Location:
        """Create a new location."""
        # Verify company exists
        company = await CompanyService.get_company(db, location.company_id)
        
        db_location = Location(**location.model_dump(), created_by_id=user_id)
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        return db_location

    @staticmethod
    async def get_location(db: Session, location_id: int) -> Location:
        """Get a location by ID."""
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        return location

    @staticmethod
    async def update_location(
        db: Session, location_id: int, location: LocationUpdate, user_id: int
    ) -> Location:
        """Update a location."""
        db_location = await LocationService.get_location(db, location_id)
        update_data = location.model_dump(exclude_unset=True)
        update_data["last_update_user_id"] = user_id
        
        for field, value in update_data.items():
            setattr(db_location, field, value)
        
        db.commit()
        db.refresh(db_location)
        return db_location

    @staticmethod
    async def list_locations(
        db: Session,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrganizationStatus] = None
    ) -> List[Location]:
        """List locations for a company with optional filtering."""
        query = db.query(Location).filter(Location.company_id == company_id)
        if status:
            query = query.filter(Location.status == status)
        return query.offset(skip).limit(limit).all()

class DepartmentService:
    """Service for department operations."""

    @staticmethod
    async def create_department(db: Session, department: DepartmentCreate, user_id: int) -> Department:
        """Create a new department."""
        # Verify company exists
        company = await CompanyService.get_company(db, department.company_id)
        
        # Verify location if provided
        if department.location_id:
            location = await LocationService.get_location(db, department.location_id)
        
        # Verify parent department if provided
        if department.parent_department_id:
            parent = await DepartmentService.get_department(db, department.parent_department_id)
            if parent.company_id != department.company_id:
                raise HTTPException(
                    status_code=400,
                    detail="Parent department must belong to the same company"
                )
        
        db_department = Department(**department.model_dump(), created_by_id=user_id)
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
        return db_department

    @staticmethod
    async def get_department(db: Session, department_id: int) -> Department:
        """Get a department by ID."""
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        return department

    @staticmethod
    async def update_department(
        db: Session, department_id: int, department: DepartmentUpdate, user_id: int
    ) -> Department:
        """Update a department."""
        db_department = await DepartmentService.get_department(db, department_id)
        update_data = department.model_dump(exclude_unset=True)
        update_data["last_update_user_id"] = user_id
        
        # Verify location if updating
        if update_data.get("location_id"):
            location = await LocationService.get_location(db, update_data["location_id"])
        
        # Verify parent department if updating
        if update_data.get("parent_department_id"):
            parent = await DepartmentService.get_department(db, update_data["parent_department_id"])
            if parent.company_id != db_department.company_id:
                raise HTTPException(
                    status_code=400,
                    detail="Parent department must belong to the same company"
                )
        
        for field, value in update_data.items():
            setattr(db_department, field, value)
        
        db.commit()
        db.refresh(db_department)
        return db_department

    @staticmethod
    async def list_departments(
        db: Session,
        company_id: int,
        location_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrganizationStatus] = None
    ) -> List[Department]:
        """List departments with optional filtering."""
        query = db.query(Department).filter(Department.company_id == company_id)
        if location_id:
            query = query.filter(Department.location_id == location_id)
        if status:
            query = query.filter(Department.status == status)
        return query.offset(skip).limit(limit).all()

class EmployeeService:
    """Service for employee operations."""

    @staticmethod
    async def create_employee(db: Session, employee: EmployeeCreate, user_id: int) -> Employee:
        """Create a new employee."""
        # Verify company exists
        company = await CompanyService.get_company(db, employee.company_id)
        
        # Verify location if provided
        if employee.location_id:
            location = await LocationService.get_location(db, employee.location_id)
        
        # Verify department if provided
        if employee.department_id:
            department = await DepartmentService.get_department(db, employee.department_id)
        
        # Create employee
        employee_data = employee.model_dump(exclude={'role_ids'})
        db_employee = Employee(**employee_data, created_by_id=user_id)
        
        # Add roles if provided
        if employee.role_ids:
            roles = db.query(Role).filter(Role.id.in_(employee.role_ids)).all()
            if len(roles) != len(employee.role_ids):
                raise HTTPException(status_code=400, detail="Invalid role IDs provided")
            db_employee.roles = roles
        
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    async def get_employee(db: Session, employee_id: int) -> Employee:
        """Get an employee by ID."""
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee

    @staticmethod
    async def update_employee(
        db: Session, employee_id: int, employee: EmployeeUpdate, user_id: int
    ) -> Employee:
        """Update an employee."""
        db_employee = await EmployeeService.get_employee(db, employee_id)
        update_data = employee.model_dump(exclude_unset=True)
        update_data["last_update_user_id"] = user_id
        
        # Handle role updates separately
        role_ids = update_data.pop('role_ids', None)
        
        # Verify location if updating
        if update_data.get("location_id"):
            location = await LocationService.get_location(db, update_data["location_id"])
        
        # Verify department if updating
        if update_data.get("department_id"):
            department = await DepartmentService.get_department(db, update_data["department_id"])
        
        # Update employee fields
        for field, value in update_data.items():
            setattr(db_employee, field, value)
        
        # Update roles if provided
        if role_ids is not None:
            roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
            if len(roles) != len(role_ids):
                raise HTTPException(status_code=400, detail="Invalid role IDs provided")
            db_employee.roles = roles
        
        db.commit()
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    async def list_employees(
        db: Session,
        company_id: int,
        location_id: Optional[int] = None,
        department_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        status: Optional[EmployeeStatus] = None
    ) -> List[Employee]:
        """List employees with optional filtering."""
        query = db.query(Employee).filter(Employee.company_id == company_id)
        if location_id:
            query = query.filter(Employee.location_id == location_id)
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        if status:
            query = query.filter(Employee.status == status)
        return query.offset(skip).limit(limit).all()

class RoleService:
    """Service for role operations."""

    @staticmethod
    async def create_role(db: Session, role: RoleCreate, user_id: int) -> Role:
        """Create a new role."""
        db_role = Role(**role.model_dump(), created_by_id=user_id)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role

    @staticmethod
    async def get_role(db: Session, role_id: int) -> Role:
        """Get a role by ID."""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    @staticmethod
    async def update_role(
        db: Session, role_id: int, role: RoleUpdate, user_id: int
    ) -> Role:
        """Update a role."""
        db_role = await RoleService.get_role(db, role_id)
        
        # System roles cannot be modified
        if db_role.is_system_role:
            raise HTTPException(status_code=400, detail="System roles cannot be modified")
        
        update_data = role.model_dump(exclude_unset=True)
        update_data["last_update_user_id"] = user_id
        
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
        return db_role

    @staticmethod
    async def list_roles(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        include_system_roles: bool = False
    ) -> List[Role]:
        """List roles with optional filtering."""
        query = db.query(Role)
        if not include_system_roles:
            query = query.filter(Role.is_system_role == False)
        return query.offset(skip).limit(limit).all()
