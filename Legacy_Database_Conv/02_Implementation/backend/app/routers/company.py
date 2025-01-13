"""
API routes for company domain operations.
Implements endpoints for managing companies, locations, departments, and employees.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import get_current_user, get_current_active_user
from ..models.company import OrganizationStatus, EmployeeStatus
from ..schemas.company import (
    CompanyCreate, CompanyUpdate, CompanyResponse,
    LocationCreate, LocationUpdate, LocationResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    RoleCreate, RoleUpdate, RoleResponse
)
from ..services.company import (
    CompanyService, LocationService,
    DepartmentService, EmployeeService,
    RoleService
)

router = APIRouter(prefix="/api/v1/company", tags=["company"])

# Company routes
@router.post("/companies/", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> CompanyResponse:
    """Create a new company."""
    return await CompanyService.create_company(db, company, current_user["id"])

@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> CompanyResponse:
    """Get a company by ID."""
    return await CompanyService.get_company(db, company_id)

@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> CompanyResponse:
    """Update a company."""
    return await CompanyService.update_company(db, company_id, company, current_user["id"])

@router.get("/companies/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[OrganizationStatus] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[CompanyResponse]:
    """List companies with optional filtering."""
    return await CompanyService.list_companies(db, skip, limit, status)

# Location routes
@router.post("/companies/{company_id}/locations/", response_model=LocationResponse)
async def create_location(
    company_id: int,
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> LocationResponse:
    """Create a new location for a company."""
    if location.company_id != company_id:
        raise HTTPException(status_code=400, detail="Company ID mismatch")
    return await LocationService.create_location(db, location, current_user["id"])

@router.get("/locations/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> LocationResponse:
    """Get a location by ID."""
    return await LocationService.get_location(db, location_id)

@router.put("/locations/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> LocationResponse:
    """Update a location."""
    return await LocationService.update_location(db, location_id, location, current_user["id"])

@router.get("/companies/{company_id}/locations/", response_model=List[LocationResponse])
async def list_locations(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[OrganizationStatus] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[LocationResponse]:
    """List locations for a company with optional filtering."""
    return await LocationService.list_locations(db, company_id, skip, limit, status)

# Department routes
@router.post("/companies/{company_id}/departments/", response_model=DepartmentResponse)
async def create_department(
    company_id: int,
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> DepartmentResponse:
    """Create a new department for a company."""
    if department.company_id != company_id:
        raise HTTPException(status_code=400, detail="Company ID mismatch")
    return await DepartmentService.create_department(db, department, current_user["id"])

@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> DepartmentResponse:
    """Get a department by ID."""
    return await DepartmentService.get_department(db, department_id)

@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> DepartmentResponse:
    """Update a department."""
    return await DepartmentService.update_department(db, department_id, department, current_user["id"])

@router.get("/companies/{company_id}/departments/", response_model=List[DepartmentResponse])
async def list_departments(
    company_id: int,
    location_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[OrganizationStatus] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[DepartmentResponse]:
    """List departments for a company with optional filtering."""
    return await DepartmentService.list_departments(db, company_id, location_id, skip, limit, status)

# Employee routes
@router.post("/companies/{company_id}/employees/", response_model=EmployeeResponse)
async def create_employee(
    company_id: int,
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> EmployeeResponse:
    """Create a new employee for a company."""
    if employee.company_id != company_id:
        raise HTTPException(status_code=400, detail="Company ID mismatch")
    return await EmployeeService.create_employee(db, employee, current_user["id"])

@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> EmployeeResponse:
    """Get an employee by ID."""
    return await EmployeeService.get_employee(db, employee_id)

@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> EmployeeResponse:
    """Update an employee."""
    return await EmployeeService.update_employee(db, employee_id, employee, current_user["id"])

@router.get("/companies/{company_id}/employees/", response_model=List[EmployeeResponse])
async def list_employees(
    company_id: int,
    location_id: Optional[int] = None,
    department_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[EmployeeStatus] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[EmployeeResponse]:
    """List employees for a company with optional filtering."""
    return await EmployeeService.list_employees(
        db, company_id, location_id, department_id, skip, limit, status
    )

# Role routes
@router.post("/roles/", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> RoleResponse:
    """Create a new role."""
    return await RoleService.create_role(db, role, current_user["id"])

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> RoleResponse:
    """Get a role by ID."""
    return await RoleService.get_role(db, role_id)

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
) -> RoleResponse:
    """Update a role."""
    return await RoleService.update_role(db, role_id, role, current_user["id"])

@router.get("/roles/", response_model=List[RoleResponse])
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_system_roles: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[RoleResponse]:
    """List roles with optional filtering."""
    return await RoleService.list_roles(db, skip, limit, include_system_roles)
