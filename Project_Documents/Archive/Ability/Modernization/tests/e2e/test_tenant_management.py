import pytest
from playwright.sync_api import Page, expect
from typing import Generator
import jwt
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.core import Tenant, Company, User
from app.services.tenant import create_tenant_with_company

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@pytest.mark.e2e
class TestTenantManagementE2E:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, db: Generator):
        # Create test data
        tenant_data = {
            "name": "E2E Test Tenant",
            "domain": "e2e.example.com",
            "company_name": "E2E Test Company",
            "admin_email": "admin@e2e.example.com",
            "admin_name": "E2E Admin"
        }
        tenant, company, admin = create_tenant_with_company(db, tenant_data)
        
        # Set access token in localStorage
        access_token = create_access_token(admin.id)
        page.context.add_cookies([{
            "name": "access_token",
            "value": access_token,
            "url": "http://localhost:3000"
        }])
        
        return tenant, company, admin

    async def test_tenant_dashboard(self, page: Page):
        # Navigate to dashboard
        await page.goto("/dashboard")
        
        # Check tenant info is displayed
        expect(page.get_by_text("E2E Test Tenant")).to_be_visible()
        expect(page.get_by_text("PROFESSIONAL")).to_be_visible()
        
        # Check statistics cards
        expect(page.get_by_text("Companies")).to_be_visible()
        expect(page.get_by_text("Active Users")).to_be_visible()
        expect(page.get_by_text("Storage Used")).to_be_visible()

    async def test_company_management(self, page: Page):
        # Navigate to companies page
        await page.goto("/companies")
        
        # Create new company
        await page.click("text=Add Company")
        await page.fill("[name=name]", "New E2E Company")
        await page.fill("[name=domain]", "new.e2e.example.com")
        await page.click("text=Create Company")
        
        # Verify company is created
        expect(page.get_by_text("New E2E Company")).to_be_visible()
        expect(page.get_by_text("new.e2e.example.com")).to_be_visible()
        
        # Edit company
        await page.click("[aria-label='Edit New E2E Company']")
        await page.fill("[name=name]", "Updated E2E Company")
        await page.click("text=Save Changes")
        
        # Verify company is updated
        expect(page.get_by_text("Updated E2E Company")).to_be_visible()
        
        # Delete company
        await page.click("[aria-label='Delete Updated E2E Company']")
        await page.click("text=Delete")
        
        # Verify company is deleted
        expect(page.get_by_text("Updated E2E Company")).not_to_be_visible()

    async def test_company_settings(self, page: Page):
        # Navigate to company settings
        await page.goto("/companies/settings")
        
        # Update company settings
        await page.select_option("select[name=theme]", "dark")
        await page.select_option("select[name=language]", "es")
        await page.click("text=Custom Branding")
        await page.click("text=Save Changes")
        
        # Verify settings are saved
        expect(page.locator("select[name=theme]")).to_have_value("dark")
        expect(page.locator("select[name=language]")).to_have_value("es")
        expect(page.get_by_label("Custom Branding")).to_be_checked()

    async def test_user_management(self, page: Page):
        # Navigate to users page
        await page.goto("/companies/users")
        
        # Invite new user
        await page.click("text=Invite User")
        await page.fill("[name=email]", "newuser@e2e.example.com")
        await page.fill("[name=fullName]", "New E2E User")
        await page.select_option("select[name=role]", "user")
        await page.fill("[name=department]", "E2E Testing")
        await page.click("text=Send Invitation")
        
        # Verify user is invited
        expect(page.get_by_text("New E2E User")).to_be_visible()
        expect(page.get_by_text("newuser@e2e.example.com")).to_be_visible()
        expect(page.get_by_text("E2E Testing")).to_be_visible()
        
        # Update user status
        await page.select_option(
            "select[aria-label='Update user status']",
            "active"
        )
        
        # Verify status is updated
        expect(page.get_by_text("active")).to_be_visible()
