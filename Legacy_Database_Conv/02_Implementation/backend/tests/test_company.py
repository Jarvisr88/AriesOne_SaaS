"""
Unit tests for company domain.
Tests models, services, and API routes for company-related operations.
"""
import pytest
from datetime import date, datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..app.models.company import (
    Company, Location, Department, Employee, Role,
    OrganizationStatus, EmployeeStatus
)
from ..app.schemas.company import (
    CompanyCreate, CompanyUpdate,
    LocationCreate, LocationUpdate,
    DepartmentCreate, DepartmentUpdate,
    EmployeeCreate, EmployeeUpdate,
    RoleCreate, RoleUpdate
)
from ..app.services.company import (
    CompanyService, LocationService,
    DepartmentService, EmployeeService,
    RoleService
)

# Test data
@pytest.fixture
def company_data():
    """Test company data."""
    return {
        "name": "Test Company",
        "code": "TEST001",
        "status": OrganizationStatus.ACTIVE,
        "phone": "123-456-7890",
        "email": "test@company.com",
        "website": "https://testcompany.com",
        "address_line1": "123 Test St",
        "city": "Test City",
        "state": "TX",
        "zip_code": "12345",
        "country": "US",
        "fiscal_year_start": 1,
        "time_zone": "America/Chicago",
        "currency": "USD"
    }

@pytest.fixture
def location_data():
    """Test location data."""
    return {
        "name": "Test Location",
        "code": "LOC001",
        "status": OrganizationStatus.ACTIVE,
        "phone": "123-456-7890",
        "email": "test@location.com",
        "address_line1": "456 Test Ave",
        "city": "Test City",
        "state": "TX",
        "zip_code": "12345",
        "country": "US",
        "is_warehouse": True,
        "is_service_center": True,
        "service_radius": 50
    }

@pytest.fixture
def department_data():
    """Test department data."""
    return {
        "name": "Test Department",
        "code": "DEPT001",
        "status": OrganizationStatus.ACTIVE,
        "department_type": "Operations",
        "cost_center": "CC001",
        "budget_code": "BUD001"
    }

@pytest.fixture
def employee_data():
    """Test employee data."""
    return {
        "employee_number": "EMP001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@company.com",
        "phone": "123-456-7890",
        "hire_date": date.today(),
        "status": EmployeeStatus.ACTIVE,
        "is_full_time": True,
        "title": "Manager",
        "role_ids": []
    }

@pytest.fixture
def role_data():
    """Test role data."""
    return {
        "name": "Test Role",
        "code": "ROLE001",
        "description": "Test role description",
        "is_system_role": False,
        "permissions": '{"read": true, "write": true}'
    }

# Company tests
class TestCompanyService:
    """Test company service operations."""

    async def test_create_company(self, db: Session, company_data):
        """Test company creation."""
        company_create = CompanyCreate(**company_data)
        company = await CompanyService.create_company(db, company_create, user_id=1)
        
        assert company.name == company_data["name"]
        assert company.code == company_data["code"]
        assert company.status == company_data["status"]
        assert company.created_by_id == 1

    async def test_get_company(self, db: Session, company_data):
        """Test company retrieval."""
        # Create test company
        company_create = CompanyCreate(**company_data)
        created_company = await CompanyService.create_company(db, company_create, user_id=1)
        
        # Test retrieval
        company = await CompanyService.get_company(db, created_company.id)
        assert company.id == created_company.id
        assert company.name == company_data["name"]

    async def test_update_company(self, db: Session, company_data):
        """Test company update."""
        # Create test company
        company_create = CompanyCreate(**company_data)
        company = await CompanyService.create_company(db, company_create, user_id=1)
        
        # Update company
        update_data = {"name": "Updated Company"}
        company_update = CompanyUpdate(**update_data)
        updated_company = await CompanyService.update_company(db, company.id, company_update, user_id=1)
        
        assert updated_company.name == update_data["name"]
        assert updated_company.last_update_user_id == 1

# Location tests
class TestLocationService:
    """Test location service operations."""

    async def test_create_location(self, db: Session, company_data, location_data):
        """Test location creation."""
        # Create test company
        company_create = CompanyCreate(**company_data)
        company = await CompanyService.create_company(db, company_create, user_id=1)
        
        # Create location
        location_data["company_id"] = company.id
        location_create = LocationCreate(**location_data)
        location = await LocationService.create_location(db, location_create, user_id=1)
        
        assert location.name == location_data["name"]
        assert location.company_id == company.id
        assert location.created_by_id == 1

    async def test_get_location(self, db: Session, company_data, location_data):
        """Test location retrieval."""
        # Create test company and location
        company_create = CompanyCreate(**company_data)
        company = await CompanyService.create_company(db, company_create, user_id=1)
        
        location_data["company_id"] = company.id
        location_create = LocationCreate(**location_data)
        created_location = await LocationService.create_location(db, location_create, user_id=1)
        
        # Test retrieval
        location = await LocationService.get_location(db, created_location.id)
        assert location.id == created_location.id
        assert location.name == location_data["name"]

# Department tests
class TestDepartmentService:
    """Test department service operations."""

    async def test_create_department(self, db: Session, company_data, department_data):
        """Test department creation."""
        # Create test company
        company_create = CompanyCreate(**company_data)
        company = await CompanyService.create_company(db, company_create, user_id=1)
        
        # Create department
        department_data["company_id"] = company.id
        department_create = DepartmentCreate(**department_data)
        department = await DepartmentService.create_department(db, department_create, user_id=1)
        
        assert department.name == department_data["name"]
        assert department.company_id == company.id
        assert department.created_by_id == 1

    async def test_department_hierarchy(self, db: Session, company_data, department_data):
        """Test department hierarchy."""
        # Create test company
        company_create = CompanyCreate(**company_data)
        company = await CompanyService.create_company(db, company_create, user_id=1)
        
        # Create parent department
        department_data["company_id"] = company.id
        parent_create = DepartmentCreate(**department_data)
        parent = await DepartmentService.create_department(db, parent_create, user_id=1)
        
        # Create child department
        child_data = department_data.copy()
        child_data["name"] = "Child Department"
        child_data["code"] = "CHILD001"
        child_data["parent_department_id"] = parent.id
        child_create = DepartmentCreate(**child_data)
        child = await DepartmentService.create_department(db, child_create, user_id=1)
        
        assert child.parent_department_id == parent.id

# Employee tests
class TestEmployeeService:
    """Test employee service operations."""

    async def test_create_employee(self, db: Session, company_data, employee_data):
        """Test employee creation."""
        # Create test company
        company_create = CompanyCreate(**company_data)
        company = await CompanyService.create_company(db, company_create, user_id=1)
        
        # Create employee
        employee_data["company_id"] = company.id
        employee_create = EmployeeCreate(**employee_data)
        employee = await EmployeeService.create_employee(db, employee_create, user_id=1)
        
        assert employee.first_name == employee_data["first_name"]
        assert employee.last_name == employee_data["last_name"]
        assert employee.company_id == company.id
        assert employee.created_by_id == 1

    async def test_employee_role_assignment(self, db: Session, company_data, employee_data, role_data):
        """Test employee role assignment."""
        # Create test company
        company_create = CompanyCreate(**company_data)
        company = await CompanyService.create_company(db, company_create, user_id=1)
        
        # Create role
        role_create = RoleCreate(**role_data)
        role = await RoleService.create_role(db, role_create, user_id=1)
        
        # Create employee with role
        employee_data["company_id"] = company.id
        employee_data["role_ids"] = [role.id]
        employee_create = EmployeeCreate(**employee_data)
        employee = await EmployeeService.create_employee(db, employee_create, user_id=1)
        
        assert len(employee.roles) == 1
        assert employee.roles[0].id == role.id

# Role tests
class TestRoleService:
    """Test role service operations."""

    async def test_create_role(self, db: Session, role_data):
        """Test role creation."""
        role_create = RoleCreate(**role_data)
        role = await RoleService.create_role(db, role_create, user_id=1)
        
        assert role.name == role_data["name"]
        assert role.code == role_data["code"]
        assert role.created_by_id == 1

    async def test_system_role_protection(self, db: Session, role_data):
        """Test system role protection."""
        # Create system role
        role_data["is_system_role"] = True
        role_create = RoleCreate(**role_data)
        role = await RoleService.create_role(db, role_create, user_id=1)
        
        # Attempt to update system role
        update_data = {"name": "Updated Role"}
        role_update = RoleUpdate(**update_data)
        
        with pytest.raises(HTTPException) as exc_info:
            await RoleService.update_role(db, role.id, role_update, user_id=1)
        assert exc_info.value.status_code == 400

# Integration tests
class TestCompanyIntegration:
    """Test company domain integration."""

    async def test_company_full_hierarchy(
        self, db: Session,
        company_data, location_data,
        department_data, employee_data, role_data
    ):
        """Test full company hierarchy creation and relationships."""
        # Create company
        company_create = CompanyCreate(**company_data)
        company = await CompanyService.create_company(db, company_create, user_id=1)
        
        # Create location
        location_data["company_id"] = company.id
        location_create = LocationCreate(**location_data)
        location = await LocationService.create_location(db, location_create, user_id=1)
        
        # Create department
        department_data["company_id"] = company.id
        department_data["location_id"] = location.id
        department_create = DepartmentCreate(**department_data)
        department = await DepartmentService.create_department(db, department_create, user_id=1)
        
        # Create role
        role_create = RoleCreate(**role_data)
        role = await RoleService.create_role(db, role_create, user_id=1)
        
        # Create employee
        employee_data["company_id"] = company.id
        employee_data["location_id"] = location.id
        employee_data["department_id"] = department.id
        employee_data["role_ids"] = [role.id]
        employee_create = EmployeeCreate(**employee_data)
        employee = await EmployeeService.create_employee(db, employee_create, user_id=1)
        
        # Verify relationships
        assert employee.company_id == company.id
        assert employee.location_id == location.id
        assert employee.department_id == department.id
        assert len(employee.roles) == 1
        assert employee.roles[0].id == role.id
        
        # Verify reverse relationships
        assert len(company.locations) == 1
        assert len(company.departments) == 1
        assert len(company.employees) == 1
        assert len(location.departments) == 1
        assert len(location.employees) == 1
        assert len(department.employees) == 1
