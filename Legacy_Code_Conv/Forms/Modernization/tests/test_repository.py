"""Repository tests.

This module tests repository layer functionality.
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    FormRepository,
    FormSubmissionRepository,
    CompanyRepository,
    CompanyFormRepository
)
from auth.models import User


@pytest.mark.asyncio
async def test_form_repository(session: AsyncSession):
    """Test form repository operations."""
    # Create test user
    user = User(
        username="form_user",
        email="form@example.com",
        hashed_password="test_hash"
    )
    session.add(user)
    await session.commit()
    
    repo = FormRepository(session)
    
    # Test creation
    form = await repo.create(
        name="Test Form",
        schema={"fields": [{"name": "field1", "type": "text"}]},
        created_by=user.id,
        description="Test Description"
    )
    
    assert form.name == "Test Form"
    assert form.schema["fields"][0]["name"] == "field1"
    
    # Test retrieval
    retrieved = await repo.get_by_id(form.id)
    assert retrieved is not None
    assert retrieved.id == form.id
    
    # Test update
    updated = await repo.update(
        form.id,
        name="Updated Form",
        description="Updated Description"
    )
    assert updated.name == "Updated Form"
    assert updated.description == "Updated Description"
    
    # Test active forms
    active_forms = await repo.get_active_forms()
    assert len(active_forms) > 0
    assert any(f.id == form.id for f in active_forms)


@pytest.mark.asyncio
async def test_form_submission_repository(session: AsyncSession):
    """Test form submission repository operations."""
    # Create test data
    user = User(
        username="sub_user",
        email="sub@example.com",
        hashed_password="test_hash"
    )
    session.add(user)
    
    company_repo = CompanyRepository(session)
    company = await company_repo.create(
        name="Sub Company",
        code="SUB002"
    )
    
    form_repo = FormRepository(session)
    form = await form_repo.create(
        name="Sub Form",
        schema={"fields": []},
        created_by=user.id
    )
    
    repo = FormSubmissionRepository(session)
    
    # Test creation
    submission = await repo.create(
        form_id=form.id,
        submitted_by=user.id,
        company_id=company.id,
        data={"field1": "test value"}
    )
    
    assert submission.form_id == form.id
    assert submission.data["field1"] == "test value"
    
    # Test retrieval
    retrieved = await repo.get_by_id(submission.id)
    assert retrieved is not None
    assert retrieved.id == submission.id
    
    # Test company submissions
    company_subs = await repo.get_company_submissions(company.id)
    assert len(company_subs) > 0
    assert any(s.id == submission.id for s in company_subs)


@pytest.mark.asyncio
async def test_company_repository(session: AsyncSession):
    """Test company repository operations."""
    repo = CompanyRepository(session)
    
    # Test creation
    company = await repo.create(
        name="Test Company",
        code="TEST002",
        settings={"theme": "light"}
    )
    
    assert company.name == "Test Company"
    assert company.code == "TEST002"
    assert company.settings["theme"] == "light"
    
    # Test retrieval by ID
    by_id = await repo.get_by_id(company.id)
    assert by_id is not None
    assert by_id.id == company.id
    
    # Test retrieval by code
    by_code = await repo.get_by_code("TEST002")
    assert by_code is not None
    assert by_code.id == company.id
    
    # Test active companies
    active = await repo.get_active_companies()
    assert len(active) > 0
    assert any(c.id == company.id for c in active)


@pytest.mark.asyncio
async def test_company_form_repository(session: AsyncSession):
    """Test company form repository operations."""
    # Create test data
    user = User(
        username="cf_user",
        email="cf@example.com",
        hashed_password="test_hash"
    )
    session.add(user)
    
    company_repo = CompanyRepository(session)
    company = await company_repo.create(
        name="CF Company",
        code="CF001"
    )
    
    form_repo = FormRepository(session)
    form = await form_repo.create(
        name="CF Form",
        schema={"fields": []},
        created_by=user.id
    )
    
    repo = CompanyFormRepository(session)
    
    # Test creation
    cf = await repo.create(
        company_id=company.id,
        form_id=form.id,
        settings={"custom_field": "value"}
    )
    
    assert cf.company_id == company.id
    assert cf.form_id == form.id
    assert cf.settings["custom_field"] == "value"
    
    # Test company forms
    company_forms = await repo.get_company_forms(company.id)
    assert len(company_forms) > 0
    assert any(c.id == cf.id for c in company_forms)
    
    # Test settings update
    updated = await repo.update_settings(
        company_id=company.id,
        form_id=form.id,
        settings={"updated_field": "new value"}
    )
    assert updated is not None
    assert updated.settings["updated_field"] == "new value"
    
    # Test get company form
    retrieved = await repo.get_company_form(company.id, form.id)
    assert retrieved is not None
    assert retrieved.id == cf.id
