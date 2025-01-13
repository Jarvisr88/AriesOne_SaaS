"""Performance tests for company operations."""
import asyncio
import time
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from locust import HttpUser, task, between

from core.models.company import Company
from infrastructure.repositories.company import CompanyRepository

@pytest.mark.performance
@pytest.mark.asyncio
async def test_bulk_company_creation(test_session: AsyncSession):
    """Test bulk company creation performance."""
    # Arrange
    repo = CompanyRepository(test_session)
    num_companies = 1000
    companies = [
        Company(
            name=f"Bulk Company {i}",
            npi=f"{i:010d}",
            tax_id=f"{i:02d}-{i:07d}",
            is_active=True
        )
        for i in range(num_companies)
    ]
    
    # Act
    start_time = time.time()
    
    for company in companies:
        await repo.add(company)
    await test_session.commit()
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Assert
    assert duration < 5.0  # Should complete within 5 seconds
    
    # Cleanup
    await test_session.rollback()

@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_company_queries(test_session: AsyncSession):
    """Test concurrent company query performance."""
    # Arrange
    repo = CompanyRepository(test_session)
    num_queries = 100
    
    # Create test company
    company = Company(
        name="Concurrent Test Company",
        npi="0000000000",
        tax_id="00-0000000",
        is_active=True
    )
    await repo.add(company)
    await test_session.commit()
    
    async def query_company():
        await repo.get_by_id(company.id)
    
    # Act
    start_time = time.time()
    
    await asyncio.gather(
        *[query_company() for _ in range(num_queries)]
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Assert
    assert duration < 2.0  # Should complete within 2 seconds
    
    # Cleanup
    await test_session.rollback()

class CompanyLoadTest(HttpUser):
    """Load test for company API."""
    
    wait_time = between(1, 2)
    
    def on_start(self):
        """Setup before tests."""
        self.headers = {
            "Authorization": "Bearer test_token"
        }
    
    @task(3)
    def get_companies(self):
        """Test GET /companies/ endpoint."""
        self.client.get(
            "/companies/",
            headers=self.headers,
            name="/companies - GET"
        )
    
    @task(2)
    def create_company(self):
        """Test POST /companies/ endpoint."""
        company_data = {
            "name": "Load Test Company",
            "npi": "1234567890",
            "tax_id": "12-3456789",
            "is_active": True
        }
        
        self.client.post(
            "/companies/",
            json=company_data,
            headers=self.headers,
            name="/companies - POST"
        )
    
    @task(1)
    def get_company(self):
        """Test GET /companies/{id} endpoint."""
        # Note: In real load test, use actual company IDs
        self.client.get(
            f"/companies/{self.company_id}",
            headers=self.headers,
            name="/companies/{id} - GET"
        )
