from typing import Optional, Tuple
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
import re

from app.models.core import Tenant, Company, TenantStatus
from app.core.config import settings
from app.db.session import SessionLocal

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip tenant resolution for public endpoints
        if self._is_public_path(request.url.path):
            return await call_next(request)

        tenant_id = None
        company_id = None

        # Try to get tenant from subdomain
        tenant, company = await self._resolve_tenant_from_host(request.headers.get("host"))
        
        if tenant:
            tenant_id = tenant.id
            if company:
                company_id = company.id
        else:
            # Try to get tenant from header
            tenant_id = request.headers.get(settings.TENANT_ID_HEADER)
            company_id = request.headers.get(settings.COMPANY_ID_HEADER)

            if not tenant_id:
                raise HTTPException(
                    status_code=400,
                    detail="Tenant identification not provided"
                )

            # Validate tenant
            db = SessionLocal()
            try:
                tenant = self._get_tenant(db, tenant_id)
                if company_id:
                    company = self._get_company(db, company_id, tenant_id)
            finally:
                db.close()

        # Set tenant context
        request.state.tenant_id = tenant_id
        request.state.company_id = company_id

        # Process request
        response = await call_next(request)

        # Add tenant headers to response
        response.headers[settings.TENANT_ID_HEADER] = str(tenant_id)
        if company_id:
            response.headers[settings.COMPANY_ID_HEADER] = str(company_id)

        return response

    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (no tenant required)"""
        public_paths = [
            r"^/docs",
            r"^/redoc",
            r"^/openapi.json",
            r"^/api/v1/auth/login",
            r"^/api/v1/auth/register",
            r"^/api/v1/tenants/register",
            r"^/health"
        ]
        return any(re.match(pattern, path) for pattern in public_paths)

    async def _resolve_tenant_from_host(
        self,
        host: Optional[str]
    ) -> Tuple[Optional[Tenant], Optional[Company]]:
        """Resolve tenant and company from host header"""
        if not host:
            return None, None

        # Remove port if present
        domain = host.split(":")[0]

        # Handle custom domains
        db = SessionLocal()
        try:
            # First try exact domain match for company
            company = db.query(Company).filter(
                Company.domain == domain
            ).first()
            
            if company:
                tenant = self._get_tenant(db, company.tenant_id)
                return tenant, company

            # Then try tenant domain
            tenant = db.query(Tenant).filter(
                Tenant.domain == domain
            ).first()
            
            if tenant:
                return tenant, None

            # Finally try subdomain matching
            if settings.TENANT_DOMAIN:
                subdomain = domain.replace(f".{settings.TENANT_DOMAIN}", "")
                if subdomain != domain:
                    tenant = db.query(Tenant).filter(
                        Tenant.name == subdomain
                    ).first()
                    if tenant:
                        return tenant, None

            return None, None
        finally:
            db.close()

    def _get_tenant(
        self,
        db: Session,
        tenant_id: str
    ) -> Tenant:
        """Get and validate tenant"""
        tenant = db.query(Tenant).filter(
            Tenant.id == tenant_id
        ).first()

        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )

        if tenant.status != TenantStatus.ACTIVE:
            raise HTTPException(
                status_code=403,
                detail=f"Tenant is {tenant.status}"
            )

        return tenant

    def _get_company(
        self,
        db: Session,
        company_id: str,
        tenant_id: str
    ) -> Company:
        """Get and validate company"""
        company = db.query(Company).filter(
            Company.id == company_id,
            Company.tenant_id == tenant_id
        ).first()

        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )

        return company
