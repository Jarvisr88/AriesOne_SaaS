"""Database repository layer.

This module provides repository classes for database access.
"""
from datetime import datetime
from typing import Optional, Sequence, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import and_

from .models import Form, FormSubmission, Company, CompanyForm


class BaseRepository:
    """Base repository with common database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: Async database session
        """
        self.session = session


class FormRepository(BaseRepository):
    """Repository for Form operations."""
    
    async def create(
        self,
        name: str,
        schema: dict,
        created_by: int,
        description: Optional[str] = None
    ) -> Form:
        """Create new form.
        
        Args:
            name: Form name
            schema: Form schema
            created_by: User ID who created the form
            description: Optional form description
            
        Returns:
            Form: Created form
        """
        form = Form(
            name=name,
            schema=schema,
            created_by=created_by,
            description=description
        )
        self.session.add(form)
        await self.session.commit()
        await self.session.refresh(form)
        return form
    
    async def get_by_id(self, form_id: int) -> Optional[Form]:
        """Get form by ID.
        
        Args:
            form_id: Form ID
            
        Returns:
            Optional[Form]: Form if found
        """
        result = await self.session.execute(
            select(Form).where(Form.id == form_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_forms(self) -> Sequence[Form]:
        """Get all active forms.
        
        Returns:
            Sequence[Form]: List of active forms
        """
        result = await self.session.execute(
            select(Form)
            .where(Form.is_active == True)
            .order_by(Form.name)
        )
        return result.scalars().all()
    
    async def update(
        self,
        form_id: int,
        **kwargs: Any
    ) -> Optional[Form]:
        """Update form attributes.
        
        Args:
            form_id: Form ID
            **kwargs: Attributes to update
            
        Returns:
            Optional[Form]: Updated form if found
        """
        await self.session.execute(
            update(Form)
            .where(Form.id == form_id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(form_id)


class FormSubmissionRepository(BaseRepository):
    """Repository for FormSubmission operations."""
    
    async def create(
        self,
        form_id: int,
        submitted_by: int,
        company_id: int,
        data: dict
    ) -> FormSubmission:
        """Create new form submission.
        
        Args:
            form_id: Form ID
            submitted_by: User ID who submitted
            company_id: Company ID
            data: Form submission data
            
        Returns:
            FormSubmission: Created submission
        """
        submission = FormSubmission(
            form_id=form_id,
            submitted_by=submitted_by,
            company_id=company_id,
            data=data
        )
        self.session.add(submission)
        await self.session.commit()
        await self.session.refresh(submission)
        return submission
    
    async def get_by_id(
        self,
        submission_id: int
    ) -> Optional[FormSubmission]:
        """Get submission by ID.
        
        Args:
            submission_id: Submission ID
            
        Returns:
            Optional[FormSubmission]: Submission if found
        """
        result = await self.session.execute(
            select(FormSubmission)
            .where(FormSubmission.id == submission_id)
        )
        return result.scalar_one_or_none()
    
    async def get_company_submissions(
        self,
        company_id: int,
        form_id: Optional[int] = None
    ) -> Sequence[FormSubmission]:
        """Get submissions for a company.
        
        Args:
            company_id: Company ID
            form_id: Optional form ID filter
            
        Returns:
            Sequence[FormSubmission]: List of submissions
        """
        query = select(FormSubmission).where(
            FormSubmission.company_id == company_id
        )
        
        if form_id:
            query = query.where(FormSubmission.form_id == form_id)
        
        result = await self.session.execute(query)
        return result.scalars().all()


class CompanyRepository(BaseRepository):
    """Repository for Company operations."""
    
    async def create(
        self,
        name: str,
        code: str,
        settings: Optional[dict] = None
    ) -> Company:
        """Create new company.
        
        Args:
            name: Company name
            code: Company code
            settings: Optional company settings
            
        Returns:
            Company: Created company
        """
        company = Company(
            name=name,
            code=code,
            settings=settings
        )
        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return company
    
    async def get_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID.
        
        Args:
            company_id: Company ID
            
        Returns:
            Optional[Company]: Company if found
        """
        result = await self.session.execute(
            select(Company).where(Company.id == company_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Company]:
        """Get company by code.
        
        Args:
            code: Company code
            
        Returns:
            Optional[Company]: Company if found
        """
        result = await self.session.execute(
            select(Company).where(Company.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_active_companies(self) -> Sequence[Company]:
        """Get all active companies.
        
        Returns:
            Sequence[Company]: List of active companies
        """
        result = await self.session.execute(
            select(Company)
            .where(Company.is_active == True)
            .order_by(Company.name)
        )
        return result.scalars().all()


class CompanyFormRepository(BaseRepository):
    """Repository for CompanyForm operations."""
    
    async def create(
        self,
        company_id: int,
        form_id: int,
        settings: Optional[dict] = None
    ) -> CompanyForm:
        """Create company-form association.
        
        Args:
            company_id: Company ID
            form_id: Form ID
            settings: Optional form settings
            
        Returns:
            CompanyForm: Created association
        """
        company_form = CompanyForm(
            company_id=company_id,
            form_id=form_id,
            settings=settings
        )
        self.session.add(company_form)
        await self.session.commit()
        await self.session.refresh(company_form)
        return company_form
    
    async def get_company_forms(
        self,
        company_id: int,
        active_only: bool = True
    ) -> Sequence[CompanyForm]:
        """Get forms for a company.
        
        Args:
            company_id: Company ID
            active_only: Only return active forms
            
        Returns:
            Sequence[CompanyForm]: List of company forms
        """
        query = select(CompanyForm).where(
            CompanyForm.company_id == company_id
        )
        
        if active_only:
            query = query.where(CompanyForm.is_active == True)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_settings(
        self,
        company_id: int,
        form_id: int,
        settings: dict
    ) -> Optional[CompanyForm]:
        """Update company-form settings.
        
        Args:
            company_id: Company ID
            form_id: Form ID
            settings: New settings
            
        Returns:
            Optional[CompanyForm]: Updated association if found
        """
        result = await self.session.execute(
            update(CompanyForm)
            .where(
                and_(
                    CompanyForm.company_id == company_id,
                    CompanyForm.form_id == form_id
                )
            )
            .values(
                settings=settings,
                updated_at=datetime.utcnow()
            )
        )
        await self.session.commit()
        
        if result.rowcount > 0:
            return await self.get_company_form(company_id, form_id)
        return None
    
    async def get_company_form(
        self,
        company_id: int,
        form_id: int
    ) -> Optional[CompanyForm]:
        """Get company-form association.
        
        Args:
            company_id: Company ID
            form_id: Form ID
            
        Returns:
            Optional[CompanyForm]: Association if found
        """
        result = await self.session.execute(
            select(CompanyForm).where(
                and_(
                    CompanyForm.company_id == company_id,
                    CompanyForm.form_id == form_id
                )
            )
        )
        return result.scalar_one_or_none()
