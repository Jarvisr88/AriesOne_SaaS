import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.core import Tenant, Company, User, TenantStatus

@pytest.mark.tenant
class TestTenantAPI:
    def test_register_tenant(self, client: TestClient, db: Session):
        response = client.post(
            "/api/v1/tenants/register",
            json={
                "name": "New Tenant",
                "domain": "new.example.com",
                "company_name": "First Company",
                "admin_email": "admin@new.example.com",
                "admin_name": "Admin User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Tenant"
        assert data["domain"] == "new.example.com"
        assert data["status"] == TenantStatus.PENDING

        # Verify database records
        tenant = db.query(Tenant).filter(Tenant.id == data["id"]).first()
        assert tenant is not None
        
        company = db.query(Company).filter(Company.tenant_id == tenant.id).first()
        assert company is not None
        assert company.name == "First Company"

        admin = db.query(User).filter(
            User.company_id == company.id,
            User.email == "admin@new.example.com"
        ).first()
        assert admin is not None
        assert admin.full_name == "Admin User"

    def test_get_current_tenant(
        self,
        client: TestClient,
        test_tenant: Tenant,
        token_headers: dict
    ):
        response = client.get("/api/v1/tenants/me", headers=token_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_tenant.id
        assert data["name"] == test_tenant.name
        assert data["domain"] == test_tenant.domain

    def test_update_tenant(
        self,
        client: TestClient,
        test_tenant: Tenant,
        token_headers: dict
    ):
        response = client.put(
            "/api/v1/tenants/me",
            headers=token_headers,
            json={
                "name": "Updated Tenant",
                "settings": {"theme": "dark"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Tenant"
        assert data["settings"]["theme"] == "dark"

    def test_get_tenant_stats(
        self,
        client: TestClient,
        test_tenant: Tenant,
        test_company: Company,
        test_user: User,
        token_headers: dict
    ):
        response = client.get(
            "/api/v1/tenants/me/stats",
            headers=token_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["company_count"] == 1
        assert data["user_count"] == 1
        assert data["active_user_count"] == 1

@pytest.mark.company
class TestCompanyAPI:
    def test_create_company(
        self,
        client: TestClient,
        test_tenant: Tenant,
        token_headers: dict
    ):
        response = client.post(
            "/api/v1/tenants/me/companies",
            headers=token_headers,
            json={
                "name": "New Company",
                "domain": "company.example.com",
                "settings": {"logo_url": "https://example.com/logo.png"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Company"
        assert data["domain"] == "company.example.com"
        assert data["settings"]["logo_url"] == "https://example.com/logo.png"

    def test_list_companies(
        self,
        client: TestClient,
        test_tenant: Tenant,
        test_company: Company,
        token_headers: dict
    ):
        response = client.get(
            "/api/v1/tenants/me/companies",
            headers=token_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == test_company.id
        assert data[0]["name"] == test_company.name

    def test_get_company(
        self,
        client: TestClient,
        test_tenant: Tenant,
        test_company: Company,
        token_headers: dict
    ):
        response = client.get(
            f"/api/v1/tenants/me/companies/{test_company.id}",
            headers=token_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id
        assert data["name"] == test_company.name

    def test_update_company(
        self,
        client: TestClient,
        test_tenant: Tenant,
        test_company: Company,
        token_headers: dict
    ):
        response = client.put(
            f"/api/v1/tenants/me/companies/{test_company.id}",
            headers=token_headers,
            json={
                "name": "Updated Company",
                "settings": {"theme": "light"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Company"
        assert data["settings"]["theme"] == "light"

    def test_delete_company(
        self,
        client: TestClient,
        test_tenant: Tenant,
        test_company: Company,
        token_headers: dict,
        db: Session
    ):
        # Create another company to avoid last company deletion restriction
        new_company = Company(
            tenant_id=test_tenant.id,
            name="Another Company",
            settings={},
            features={}
        )
        db.add(new_company)
        db.commit()

        response = client.delete(
            f"/api/v1/tenants/me/companies/{test_company.id}",
            headers=token_headers
        )
        assert response.status_code == 200

        # Verify company is deleted
        company = db.query(Company).filter(Company.id == test_company.id).first()
        assert company is None

    def test_cannot_delete_last_company(
        self,
        client: TestClient,
        test_tenant: Tenant,
        test_company: Company,
        token_headers: dict
    ):
        response = client.delete(
            f"/api/v1/tenants/me/companies/{test_company.id}",
            headers=token_headers
        )
        assert response.status_code == 400
        assert "last company" in response.json()["detail"].lower()
