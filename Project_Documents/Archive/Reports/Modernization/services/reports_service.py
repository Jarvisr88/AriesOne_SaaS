"""Reports services."""
from datetime import datetime
import re
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.reports_models import (
    Report,
    ReportTemplate,
    ReportHistory,
    ReportTemplateHistory,
    ReportType,
    ReportFormat,
    ReportCreate,
    ReportUpdate,
    ReportTemplateCreate,
    ReportTemplateUpdate
)


class ReportService:
    """Report service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def get_reports(
        self,
        category: Optional[str] = None,
        include_deleted: bool = False
    ) -> List[Report]:
        """Get all reports.
        
        Args:
            category: Category filter
            include_deleted: Include deleted reports
            
        Returns:
            List of reports
        """
        query = select(Report)
        if category:
            query = query.where(Report.category == category)
        if not include_deleted:
            query = query.where(Report.is_deleted.is_(False))
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_report(
        self,
        report_id: int,
        include_deleted: bool = False
    ) -> Optional[Report]:
        """Get report by ID.
        
        Args:
            report_id: Report ID
            include_deleted: Include deleted reports
            
        Returns:
            Report if found
            
        Raises:
            HTTPException: If not found
        """
        query = select(Report).where(Report.id == report_id)
        if not include_deleted:
            query = query.where(Report.is_deleted.is_(False))
        
        result = await self.session.execute(query)
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        return report
    
    async def create_report(
        self,
        data: ReportCreate,
        user_id: int
    ) -> Report:
        """Create report.
        
        Args:
            data: Report data
            user_id: Creating user ID
            
        Returns:
            Created report
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate template
        if data.template_id:
            template = await self.get_template(data.template_id)
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Template not found"
                )
        
        report = Report(
            name=data.name,
            category=data.category,
            file_name=data.file_name,
            type=data.type,
            is_system=data.is_system,
            template_id=data.template_id,
            parameters=data.parameters,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.session.add(report)
        await self.session.commit()
        return report
    
    async def update_report(
        self,
        report_id: int,
        data: ReportUpdate,
        user_id: int
    ) -> Report:
        """Update report.
        
        Args:
            report_id: Report ID
            data: Update data
            user_id: Updating user ID
            
        Returns:
            Updated report
            
        Raises:
            HTTPException: If not found or validation fails
        """
        report = await self.get_report(report_id)
        
        # Create history record
        history = ReportHistory(
            report_id=report.id,
            name=report.name,
            category=report.category,
            file_name=report.file_name,
            type=report.type,
            is_system=report.is_system,
            template_id=report.template_id,
            parameters=report.parameters,
            created_by=user_id,
            reason=data.reason
        )
        self.session.add(history)
        
        # Update report
        if data.name is not None:
            report.name = data.name
        if data.category is not None:
            report.category = data.category
        if data.parameters is not None:
            report.parameters = data.parameters
        
        report.updated_by = user_id
        report.version += 1
        
        await self.session.commit()
        return report
    
    async def delete_report(
        self,
        report_id: int,
        user_id: int
    ) -> None:
        """Delete report.
        
        Args:
            report_id: Report ID
            user_id: Deleting user ID
            
        Raises:
            HTTPException: If not found
        """
        report = await self.get_report(report_id)
        
        if report.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete system report"
            )
        
        report.is_deleted = True
        report.deleted_at = datetime.utcnow()
        report.deleted_by = user_id
        report.updated_by = user_id
        report.version += 1
        
        await self.session.commit()
    
    async def restore_report(
        self,
        report_id: int,
        user_id: int
    ) -> Report:
        """Restore deleted report.
        
        Args:
            report_id: Report ID
            user_id: Restoring user ID
            
        Returns:
            Restored report
            
        Raises:
            HTTPException: If not found
        """
        report = await self.get_report(report_id, include_deleted=True)
        
        report.is_deleted = False
        report.deleted_at = None
        report.deleted_by = None
        report.updated_by = user_id
        report.version += 1
        
        await self.session.commit()
        return report
    
    async def get_report_history(
        self,
        report_id: int
    ) -> List[ReportHistory]:
        """Get report history.
        
        Args:
            report_id: Report ID
            
        Returns:
            List of history records
            
        Raises:
            HTTPException: If not found
        """
        report = await self.get_report(report_id)
        return report.history


class ReportTemplateService:
    """Report template service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service.
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def get_templates(
        self,
        category: Optional[str] = None
    ) -> List[ReportTemplate]:
        """Get all templates.
        
        Args:
            category: Category filter
            
        Returns:
            List of templates
        """
        query = select(ReportTemplate)
        if category:
            query = query.where(ReportTemplate.category == category)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_template(
        self,
        template_id: int
    ) -> Optional[ReportTemplate]:
        """Get template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template if found
            
        Raises:
            HTTPException: If not found
        """
        query = select(ReportTemplate).where(
            ReportTemplate.id == template_id
        )
        result = await self.session.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return template
    
    async def create_template(
        self,
        data: ReportTemplateCreate,
        user_id: int
    ) -> ReportTemplate:
        """Create template.
        
        Args:
            data: Template data
            user_id: Creating user ID
            
        Returns:
            Created template
            
        Raises:
            HTTPException: If validation fails
        """
        template = ReportTemplate(
            name=data.name,
            category=data.category,
            file_name=data.file_name,
            is_system=data.is_system,
            parameters=data.parameters,
            content=data.content,
            format=data.format,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.session.add(template)
        await self.session.commit()
        return template
    
    async def update_template(
        self,
        template_id: int,
        data: ReportTemplateUpdate,
        user_id: int
    ) -> ReportTemplate:
        """Update template.
        
        Args:
            template_id: Template ID
            data: Update data
            user_id: Updating user ID
            
        Returns:
            Updated template
            
        Raises:
            HTTPException: If not found or validation fails
        """
        template = await self.get_template(template_id)
        
        if template.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify system template"
            )
        
        # Create history record
        history = ReportTemplateHistory(
            template_id=template.id,
            name=template.name,
            category=template.category,
            file_name=template.file_name,
            is_system=template.is_system,
            parameters=template.parameters,
            content=template.content,
            format=template.format,
            created_by=user_id,
            reason=data.reason
        )
        self.session.add(history)
        
        # Update template
        if data.name is not None:
            template.name = data.name
        if data.category is not None:
            template.category = data.category
        if data.parameters is not None:
            template.parameters = data.parameters
        if data.content is not None:
            template.content = data.content
        if data.format is not None:
            template.format = data.format
        
        template.updated_by = user_id
        template.version += 1
        
        await self.session.commit()
        return template
    
    async def delete_template(
        self,
        template_id: int,
        user_id: int
    ) -> None:
        """Delete template.
        
        Args:
            template_id: Template ID
            user_id: Deleting user ID
            
        Raises:
            HTTPException: If not found or has dependencies
        """
        template = await self.get_template(template_id)
        
        if template.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete system template"
            )
        
        # Check for dependencies
        query = select(Report).where(Report.template_id == template_id)
        result = await self.session.execute(query)
        if result.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template is in use by reports"
            )
        
        await self.session.delete(template)
        await self.session.commit()
    
    async def get_template_history(
        self,
        template_id: int
    ) -> List[ReportTemplateHistory]:
        """Get template history.
        
        Args:
            template_id: Template ID
            
        Returns:
            List of history records
            
        Raises:
            HTTPException: If not found
        """
        template = await self.get_template(template_id)
        return template.history
