"""Schema validation tests.

This module tests database schema and models.
"""
import pytest
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Form, FormSubmission, Company, CompanyForm
from auth.models import User


@pytest.mark.asyncio
async def test_form_creation(session: AsyncSession):
    """Test form creation with valid data."""
    # Create test user
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="test_hash"
    )
    session.add(user)
    await session.commit()
    
    # Create form
    form = Form(
        name="Test Form",
        description="Test Description",
        schema={"fields": []},
        created_by=user.id
    )
    session.add(form)
    await session.commit()
    
    # Verify form
    result = await session.execute(
        select(Form).where(Form.id == form.id)
    )
    saved_form = result.scalar_one()
    
    assert saved_form.name == "Test Form"
    assert saved_form.description == "Test Description"
    assert saved_form.schema == {"fields": []}
    assert saved_form.created_by == user.id
    assert saved_form.is_active == True
    assert isinstance(saved_form.created_at, datetime)
    assert isinstance(saved_form.updated_at, datetime)


@pytest.mark.asyncio
async def test_company_creation(session: AsyncSession):
    """Test company creation with valid data."""
    company = Company(
        name="Test Company",
        code="TEST001",
        settings={"theme": "dark"}
    )
    session.add(company)
    await session.commit()
    
    result = await session.execute(
        select(Company).where(Company.id == company.id)
    )
    saved_company = result.scalar_one()
    
    assert saved_company.name == "Test Company"
    assert saved_company.code == "TEST001"
    assert saved_company.settings == {"theme": "dark"}
    assert saved_company.is_active == True


@pytest.mark.asyncio
async def test_form_submission(session: AsyncSession):
    """Test form submission with valid data."""
    # Create test user
    user = User(
        username="submitter",
        email="submitter@example.com",
        hashed_password="test_hash"
    )
    session.add(user)
    
    # Create test company
    company = Company(
        name="Submit Co",
        code="SUB001"
    )
    session.add(company)
    
    # Create test form
    form = Form(
        name="Submit Form",
        schema={"fields": []},
        created_by=user.id
    )
    session.add(form)
    await session.commit()
    
    # Create submission
    submission = FormSubmission(
        form_id=form.id,
        submitted_by=user.id,
        company_id=company.id,
        data={"field1": "value1"}
    )
    session.add(submission)
    await session.commit()
    
    result = await session.execute(
        select(FormSubmission).where(FormSubmission.id == submission.id)
    )
    saved_submission = result.scalar_one()
    
    assert saved_submission.form_id == form.id
    assert saved_submission.submitted_by == user.id
    assert saved_submission.company_id == company.id
    assert saved_submission.data == {"field1": "value1"}
    assert isinstance(saved_submission.submitted_at, datetime)


@pytest.mark.asyncio
async def test_company_form_association(session: AsyncSession):
    """Test company-form association with settings."""
    # Create test user
    user = User(
        username="assoc_user",
        email="assoc@example.com",
        hashed_password="test_hash"
    )
    session.add(user)
    
    # Create test company
    company = Company(
        name="Assoc Co",
        code="ASC001"
    )
    session.add(company)
    
    # Create test form
    form = Form(
        name="Assoc Form",
        schema={"fields": []},
        created_by=user.id
    )
    session.add(form)
    await session.commit()
    
    # Create association
    company_form = CompanyForm(
        company_id=company.id,
        form_id=form.id,
        settings={"custom_theme": "light"}
    )
    session.add(company_form)
    await session.commit()
    
    result = await session.execute(
        select(CompanyForm).where(CompanyForm.id == company_form.id)
    )
    saved_assoc = result.scalar_one()
    
    assert saved_assoc.company_id == company.id
    assert saved_assoc.form_id == form.id
    assert saved_assoc.settings == {"custom_theme": "light"}
    assert saved_assoc.is_active == True


@pytest.mark.asyncio
async def test_cascade_delete(session: AsyncSession):
    """Test cascade delete behavior."""
    # Create test data
    user = User(
        username="cascade_user",
        email="cascade@example.com",
        hashed_password="test_hash"
    )
    session.add(user)
    
    company = Company(
        name="Cascade Co",
        code="CAS001"
    )
    session.add(company)
    
    form = Form(
        name="Cascade Form",
        schema={"fields": []},
        created_by=user.id
    )
    session.add(form)
    await session.commit()
    
    # Create submissions and associations
    submission = FormSubmission(
        form_id=form.id,
        submitted_by=user.id,
        company_id=company.id,
        data={}
    )
    session.add(submission)
    
    company_form = CompanyForm(
        company_id=company.id,
        form_id=form.id
    )
    session.add(company_form)
    await session.commit()
    
    # Delete form and verify cascade
    await session.delete(form)
    await session.commit()
    
    # Verify deletions
    result = await session.execute(
        select(FormSubmission).where(FormSubmission.id == submission.id)
    )
    assert result.scalar_one_or_none() is None
    
    result = await session.execute(
        select(CompanyForm).where(CompanyForm.id == company_form.id)
    )
    assert result.scalar_one_or_none() is None
