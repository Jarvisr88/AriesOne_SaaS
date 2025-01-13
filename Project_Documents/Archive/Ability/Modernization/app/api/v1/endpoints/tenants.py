from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.api import deps
from app.models.core import (
    Tenant,
    Company,
    TenantStatus,
    SubscriptionTier,
    User,
    AuditLogType
)
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    TenantStats
)
from app.services.audit import AuditService
from app.services.config import ConfigurationService
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=TenantResponse)
async def register_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_in: TenantCreate,
    request: Request,
    audit_service: AuditService = Depends(deps.get_audit_service)
):
    """Register a new tenant"""
    # Check if domain is available
    if tenant_in.domain:
        existing = db.query(Tenant).filter(Tenant.domain == tenant_in.domain).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Domain already registered"
            )

    # Create tenant
    tenant = Tenant(
        name=tenant_in.name,
        domain=tenant_in.domain,
        status=TenantStatus.PENDING,
        subscription_tier=SubscriptionTier.FREE,
        settings=tenant_in.settings or {},
        features=settings.DEFAULT_TENANT_FEATURES
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    # Create initial company
    company = Company(
        tenant_id=tenant.id,
        name=tenant_in.company_name,
        settings={},
        features={}
    )
    db.add(company)

    # Create admin user
    admin_user = User(
        company_id=company.id,
        email=tenant_in.admin_email,
        full_name=tenant_in.admin_name,
        status="active",
        settings={}
    )
    db.add(admin_user)
    
    db.commit()

    # Log tenant creation
    await audit_service.log_event(
        tenant_id=tenant.id,
        company_id=company.id,
        user_id=admin_user.id,
        log_type=AuditLogType.ADMIN,
        action="tenant_create",
        status="success",
        request=request,
        new_values={
            "tenant_name": tenant.name,
            "domain": tenant.domain,
            "company_name": company.name,
            "admin_email": admin_user.email
        }
    )

    return tenant

@router.get("/me", response_model=TenantResponse)
async def get_current_tenant(
    *,
    db: Session = Depends(deps.get_db),
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
):
    """Get current tenant details"""
    tenant = db.query(Tenant).filter(Tenant.id == current_tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.put("/me", response_model=TenantResponse)
async def update_current_tenant(
    *,
    db: Session = Depends(deps.get_db),
    tenant_in: TenantUpdate,
    current_tenant_id: int = Depends(deps.get_current_tenant_id),
    current_user: User = Depends(deps.get_current_user),
    request: Request,
    audit_service: AuditService = Depends(deps.get_audit_service)
):
    """Update current tenant"""
    tenant = db.query(Tenant).filter(Tenant.id == current_tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    old_values = {
        "name": tenant.name,
        "domain": tenant.domain,
        "settings": tenant.settings
    }

    # Update fields
    if tenant_in.name is not None:
        tenant.name = tenant_in.name
    if tenant_in.domain is not None:
        # Check domain availability
        existing = db.query(Tenant).filter(
            Tenant.domain == tenant_in.domain,
            Tenant.id != tenant.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Domain already registered"
            )
        tenant.domain = tenant_in.domain
    if tenant_in.settings is not None:
        tenant.settings.update(tenant_in.settings)

    tenant.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(tenant)

    # Log update
    await audit_service.log_event(
        tenant_id=tenant.id,
        user_id=current_user.id,
        log_type=AuditLogType.ADMIN,
        action="tenant_update",
        status="success",
        request=request,
        old_values=old_values,
        new_values={
            "name": tenant.name,
            "domain": tenant.domain,
            "settings": tenant.settings
        }
    )

    return tenant

@router.get("/me/stats", response_model=TenantStats)
async def get_tenant_stats(
    *,
    db: Session = Depends(deps.get_db),
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
):
    """Get tenant statistics"""
    # Get counts
    company_count = db.query(Company).filter(
        Company.tenant_id == current_tenant_id
    ).count()
    
    user_count = db.query(User).join(
        Company, Company.id == User.company_id
    ).filter(
        Company.tenant_id == current_tenant_id
    ).count()

    active_user_count = db.query(User).join(
        Company, Company.id == User.company_id
    ).filter(
        Company.tenant_id == current_tenant_id,
        User.status == "active"
    ).count()

    # Get storage usage
    storage_usage = 0  # Implement storage calculation

    return {
        "company_count": company_count,
        "user_count": user_count,
        "active_user_count": active_user_count,
        "storage_usage": storage_usage
    }

@router.post("/me/companies", response_model=CompanyResponse)
async def create_company(
    *,
    db: Session = Depends(deps.get_db),
    company_in: CompanyCreate,
    current_tenant_id: int = Depends(deps.get_current_tenant_id),
    current_user: User = Depends(deps.get_current_user),
    request: Request,
    audit_service: AuditService = Depends(deps.get_audit_service)
):
    """Create new company in tenant"""
    # Check company limit
    company_count = db.query(Company).filter(
        Company.tenant_id == current_tenant_id
    ).count()
    
    tenant = db.query(Tenant).filter(Tenant.id == current_tenant_id).first()
    if company_count >= settings.COMPANY_LIMITS[tenant.subscription_tier]:
        raise HTTPException(
            status_code=403,
            detail="Company limit reached for subscription tier"
        )

    # Create company
    company = Company(
        tenant_id=current_tenant_id,
        name=company_in.name,
        domain=company_in.domain,
        settings=company_in.settings or {},
        features=company_in.features or {}
    )
    db.add(company)
    db.commit()
    db.refresh(company)

    # Log company creation
    await audit_service.log_event(
        tenant_id=current_tenant_id,
        company_id=company.id,
        user_id=current_user.id,
        log_type=AuditLogType.ADMIN,
        action="company_create",
        status="success",
        request=request,
        new_values={
            "name": company.name,
            "domain": company.domain,
            "settings": company.settings,
            "features": company.features
        }
    )

    return company

@router.get("/me/companies", response_model=List[CompanyResponse])
async def list_companies(
    *,
    db: Session = Depends(deps.get_db),
    current_tenant_id: int = Depends(deps.get_current_tenant_id),
    skip: int = 0,
    limit: int = 100
):
    """List companies in tenant"""
    companies = db.query(Company).filter(
        Company.tenant_id == current_tenant_id
    ).offset(skip).limit(limit).all()
    
    return companies

@router.get("/me/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    current_tenant_id: int = Depends(deps.get_current_tenant_id)
):
    """Get company details"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == current_tenant_id
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return company

@router.put("/me/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    company_in: CompanyUpdate,
    current_tenant_id: int = Depends(deps.get_current_tenant_id),
    current_user: User = Depends(deps.get_current_user),
    request: Request,
    audit_service: AuditService = Depends(deps.get_audit_service)
):
    """Update company details"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == current_tenant_id
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    old_values = {
        "name": company.name,
        "domain": company.domain,
        "settings": company.settings,
        "features": company.features
    }

    # Update fields
    if company_in.name is not None:
        company.name = company_in.name
    if company_in.domain is not None:
        company.domain = company_in.domain
    if company_in.settings is not None:
        company.settings.update(company_in.settings)
    if company_in.features is not None:
        company.features.update(company_in.features)

    company.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(company)

    # Log update
    await audit_service.log_event(
        tenant_id=current_tenant_id,
        company_id=company.id,
        user_id=current_user.id,
        log_type=AuditLogType.ADMIN,
        action="company_update",
        status="success",
        request=request,
        old_values=old_values,
        new_values={
            "name": company.name,
            "domain": company.domain,
            "settings": company.settings,
            "features": company.features
        }
    )

    return company

@router.delete("/me/companies/{company_id}")
async def delete_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    current_tenant_id: int = Depends(deps.get_current_tenant_id),
    current_user: User = Depends(deps.get_current_user),
    request: Request,
    audit_service: AuditService = Depends(deps.get_audit_service)
):
    """Delete company"""
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == current_tenant_id
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if it's the last company
    company_count = db.query(Company).filter(
        Company.tenant_id == current_tenant_id
    ).count()
    
    if company_count <= 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the last company in tenant"
        )

    # Log deletion
    await audit_service.log_event(
        tenant_id=current_tenant_id,
        company_id=company.id,
        user_id=current_user.id,
        log_type=AuditLogType.ADMIN,
        action="company_delete",
        status="success",
        request=request,
        old_values={
            "name": company.name,
            "domain": company.domain
        }
    )

    # Delete company
    db.delete(company)
    db.commit()

    return {"status": "success"}
