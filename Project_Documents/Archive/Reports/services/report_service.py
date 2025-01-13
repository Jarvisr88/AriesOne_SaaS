"""Report service module."""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, BackgroundTasks
from ..models.report import Report, ReportExecution, ReportTemplate
from ..schemas.report import ReportCreate, ReportUpdate, ReportExecutionCreate
from app.core.security import get_current_user_id

class ReportService:
    """Service for handling report operations."""

    def __init__(self, db: Session):
        """Initialize report service."""
        self.db = db

    def create_report(self, data: ReportCreate, user_id: int) -> Report:
        """Create a new report."""
        report = Report(
            name=data.name,
            category=data.category,
            file_name=data.file_name,
            description=data.description,
            parameters=data.parameters,
            created_by=user_id
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_report(self, report_id: int) -> Optional[Report]:
        """Get a report by ID."""
        return self.db.query(Report).filter(
            Report.id == report_id,
            Report.is_deleted == False
        ).first()

    def get_reports(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        """Get all reports with optional filtering."""
        query = self.db.query(Report).filter(Report.is_deleted == False)

        if category:
            query = query.filter(Report.category == category)
        
        if search:
            query = query.filter(or_(
                Report.name.ilike(f"%{search}%"),
                Report.description.ilike(f"%{search}%")
            ))

        return query.offset(skip).limit(limit).all()

    def update_report(
        self,
        report_id: int,
        data: ReportUpdate,
        user_id: int
    ) -> Optional[Report]:
        """Update a report."""
        report = self.get_report(report_id)
        if not report:
            return None

        for field, value in data.dict(exclude_unset=True).items():
            setattr(report, field, value)

        report.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(report)
        return report

    def delete_report(self, report_id: int) -> bool:
        """Soft delete a report."""
        report = self.get_report(report_id)
        if not report:
            return False

        report.is_deleted = True
        report.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def execute_report(
        self,
        report_id: int,
        data: ReportExecutionCreate,
        user_id: int,
        background_tasks: BackgroundTasks
    ) -> ReportExecution:
        """Execute a report asynchronously."""
        report = self.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        execution = ReportExecution(
            report_id=report_id,
            user_id=user_id,
            status="pending",
            parameters=data.parameters
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        # Add report execution to background tasks
        background_tasks.add_task(
            self._process_report_execution,
            execution.id,
            data.parameters
        )

        return execution

    async def _process_report_execution(
        self,
        execution_id: int,
        parameters: Dict[str, Any]
    ):
        """Process report execution in background."""
        execution = self.db.query(ReportExecution).get(execution_id)
        if not execution:
            return

        try:
            execution.status = "running"
            execution.started_at = datetime.utcnow()
            self.db.commit()

            # Get report template
            report = execution.report
            template = self.db.query(ReportTemplate).filter(
                ReportTemplate.id == report.template_id
            ).first()

            if not template:
                raise ValueError("Report template not found")

            # Generate report based on template type
            if template.template_type == "sql":
                result_file = await self._generate_sql_report(
                    template, parameters
                )
            elif template.template_type == "jinja":
                result_file = await self._generate_jinja_report(
                    template, parameters
                )
            else:
                result_file = await self._generate_custom_report(
                    template, parameters
                )

            execution.status = "completed"
            execution.result_file = result_file
            execution.completed_at = datetime.utcnow()

        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()

        finally:
            self.db.commit()

    async def _generate_sql_report(
        self,
        template: ReportTemplate,
        parameters: Dict[str, Any]
    ) -> str:
        """Generate report from SQL template."""
        # Implementation for SQL-based reports
        pass

    async def _generate_jinja_report(
        self,
        template: ReportTemplate,
        parameters: Dict[str, Any]
    ) -> str:
        """Generate report from Jinja template."""
        # Implementation for Jinja template-based reports
        pass

    async def _generate_custom_report(
        self,
        template: ReportTemplate,
        parameters: Dict[str, Any]
    ) -> str:
        """Generate report using custom logic."""
        # Implementation for custom report generation
        pass
