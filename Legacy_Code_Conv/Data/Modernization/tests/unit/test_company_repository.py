"""Unit tests for company repository."""
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.company import Company
from infrastructure.repositories.company import CompanyRepository

@pytest.mark.asyncio
async def test_create_company(test_session: AsyncSession):
    """Test company creation."""
    # Arrange
    repo = CompanyRepository(test_session)
    company_data = {
        "name": "Test Company",
        "npi": "1234567890",
        "tax_id": "12-3456789",
        "is_active": True
    }
    
    # Act
    company = Company(**company_data)
    await repo.add(company)
    await test_session.commit()
    
    # Assert
    saved_company = await repo.get_by_id(company.id)
    assert saved_company is not None
    assert saved_company.name == company_data["name"]
    assert saved_company.npi == company_data["npi"]

@pytest.mark.asyncio
async def test_get_by_npi(test_session: AsyncSession):
    """Test getting company by NPI."""
    # Arrange
    repo = CompanyRepository(test_session)
    company = Company(
        name="Test Company",
        npi="9876543210",
        tax_id="98-7654321",
        is_active=True
    )
    await repo.add(company)
    await test_session.commit()
    
    # Act
    result = await repo.get_by_npi("9876543210")
    
    # Assert
    assert result is not None
    assert result.id == company.id
    assert result.npi == "9876543210"

@pytest.mark.asyncio
async def test_get_active_companies(test_session: AsyncSession):
    """Test getting active companies."""
    # Arrange
    repo = CompanyRepository(test_session)
    companies = [
        Company(
            name="Active Company 1",
            npi="1111111111",
            tax_id="11-1111111",
            is_active=True
        ),
        Company(
            name="Active Company 2",
            npi="2222222222",
            tax_id="22-2222222",
            is_active=True
        ),
        Company(
            name="Inactive Company",
            npi="3333333333",
            tax_id="33-3333333",
            is_active=False
        )
    ]
    
    for company in companies:
        await repo.add(company)
    await test_session.commit()
    
    # Act
    active_companies = await repo.get_active_companies()
    
    # Assert
    assert len(active_companies) == 2
    assert all(c.is_active for c in active_companies)

@pytest.mark.asyncio
async def test_soft_delete_company(test_session: AsyncSession):
    """Test soft deleting company."""
    # Arrange
    repo = CompanyRepository(test_session)
    company = Company(
        name="Company to Delete",
        npi="4444444444",
        tax_id="44-4444444",
        is_active=True
    )
    await repo.add(company)
    await test_session.commit()
    
    # Act
    await repo.soft_delete(company.id)
    await test_session.commit()
    
    # Assert
    deleted_company = await repo.get_by_id(company.id)
    assert deleted_company is not None
    assert deleted_company.is_deleted is True

@pytest.mark.asyncio
async def test_update_company(test_session: AsyncSession):
    """Test updating company."""
    # Arrange
    repo = CompanyRepository(test_session)
    company = Company(
        name="Original Name",
        npi="5555555555",
        tax_id="55-5555555",
        is_active=True
    )
    await repo.add(company)
    await test_session.commit()
    
    # Act
    company.name = "Updated Name"
    await repo.update(company)
    await test_session.commit()
    
    # Assert
    updated_company = await repo.get_by_id(company.id)
    assert updated_company is not None
    assert updated_company.name == "Updated Name"

@pytest.mark.asyncio
async def test_get_nonexistent_company(test_session: AsyncSession):
    """Test getting nonexistent company."""
    # Arrange
    repo = CompanyRepository(test_session)
    random_id = uuid.uuid4()
    
    # Act
    result = await repo.get_by_id(random_id)
    
    # Assert
    assert result is None
