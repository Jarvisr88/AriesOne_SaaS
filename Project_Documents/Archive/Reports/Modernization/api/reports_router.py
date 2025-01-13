"""Reports API router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...Core.Modernization.api.deps import (
    get_current_user,
    get_db,
    verify_permission
)
from ...Core.Modernization.models.users import User
from ..models.reports_models import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportTemplateResponse,
    ReportHistoryResponse,
    ReportTemplateHistoryResponse
)
from ..services.reports_service import (
    ReportService,
    ReportTemplateService
)


router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)


@router.get(
    "",
    response_model=List[ReportResponse],
    dependencies=[Depends(verify_permission("reports.view"))]
)
async def get_reports(
    category: Optional[str] = None,
    include_deleted: bool = False,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ReportResponse]:
    """Get all reports.
    
    Args:
        category: Category filter
        include_deleted: Include deleted reports
        session: Database session
        current_user: Current user
        
    Returns:
        List of reports
    """
    service = ReportService(session)
    reports = await service.get_reports(category, include_deleted)
    return reports


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    dependencies=[Depends(verify_permission("reports.view"))]
)
async def get_report(
    report_id: int,
    include_deleted: bool = False,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """Get report by ID.
    
    Args:
        report_id: Report ID
        include_deleted: Include deleted reports
        session: Database session
        current_user: Current user
        
    Returns:
        Report if found
        
    Raises:
        HTTPException: If not found
    """
    service = ReportService(session)
    report = await service.get_report(report_id, include_deleted)
    return report


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_permission("reports.create"))]
)
async def create_report(
    data: ReportCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """Create report.
    
    Args:
        data: Report data
        session: Database session
        current_user: Current user
        
    Returns:
        Created report
        
    Raises:
        HTTPException: If validation fails
    """
    service = ReportService(session)
    report = await service.create_report(data, current_user.id)
    return report


@router.put(
    "/{report_id}",
    response_model=ReportResponse,
    dependencies=[Depends(verify_permission("reports.edit"))]
)
async def update_report(
    report_id: int,
    data: ReportUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """Update report.
    
    Args:
        report_id: Report ID
        data: Update data
        session: Database session
        current_user: Current user
        
    Returns:
        Updated report
        
    Raises:
        HTTPException: If not found or validation fails
    """
    service = ReportService(session)
    report = await service.update_report(report_id, data, current_user.id)
    return report


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_permission("reports.delete"))]
)
async def delete_report(
    report_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete report.
    
    Args:
        report_id: Report ID
        session: Database session
        current_user: Current user
        
    Raises:
        HTTPException: If not found
    """
    service = ReportService(session)
    await service.delete_report(report_id, current_user.id)


@router.post(
    "/{report_id}/restore",
    response_model=ReportResponse,
    dependencies=[Depends(verify_permission("reports.edit"))]
)
async def restore_report(
    report_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """Restore deleted report.
    
    Args:
        report_id: Report ID
        session: Database session
        current_user: Current user
        
    Returns:
        Restored report
        
    Raises:
        HTTPException: If not found
    """
    service = ReportService(session)
    report = await service.restore_report(report_id, current_user.id)
    return report


@router.get(
    "/{report_id}/history",
    response_model=List[ReportHistoryResponse],
    dependencies=[Depends(verify_permission("reports.view"))]
)
async def get_report_history(
    report_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ReportHistoryResponse]:
    """Get report history.
    
    Args:
        report_id: Report ID
        session: Database session
        current_user: Current user
        
    Returns:
        List of history records
        
    Raises:
        HTTPException: If not found
    """
    service = ReportService(session)
    history = await service.get_report_history(report_id)
    return history


# Template endpoints
@router.get(
    "/templates",
    response_model=List[ReportTemplateResponse],
    dependencies=[Depends(verify_permission("templates.view"))]
)
async def get_templates(
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ReportTemplateResponse]:
    """Get all templates.
    
    Args:
        category: Category filter
        session: Database session
        current_user: Current user
        
    Returns:
        List of templates
    """
    service = ReportTemplateService(session)
    templates = await service.get_templates(category)
    return templates


@router.get(
    "/templates/{template_id}",
    response_model=ReportTemplateResponse,
    dependencies=[Depends(verify_permission("templates.view"))]
)
async def get_template(
    template_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportTemplateResponse:
    """Get template by ID.
    
    Args:
        template_id: Template ID
        session: Database session
        current_user: Current user
        
    Returns:
        Template if found
        
    Raises:
        HTTPException: If not found
    """
    service = ReportTemplateService(session)
    template = await service.get_template(template_id)
    return template


@router.post(
    "/templates",
    response_model=ReportTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_permission("templates.create"))]
)
async def create_template(
    data: ReportTemplateCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportTemplateResponse:
    """Create template.
    
    Args:
        data: Template data
        session: Database session
        current_user: Current user
        
    Returns:
        Created template
        
    Raises:
        HTTPException: If validation fails
    """
    service = ReportTemplateService(session)
    template = await service.create_template(data, current_user.id)
    return template


@router.put(
    "/templates/{template_id}",
    response_model=ReportTemplateResponse,
    dependencies=[Depends(verify_permission("templates.edit"))]
)
async def update_template(
    template_id: int,
    data: ReportTemplateUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportTemplateResponse:
    """Update template.
    
    Args:
        template_id: Template ID
        data: Update data
        session: Database session
        current_user: Current user
        
    Returns:
        Updated template
        
    Raises:
        HTTPException: If not found or validation fails
    """
    service = ReportTemplateService(session)
    template = await service.update_template(
        template_id,
        data,
        current_user.id
    )
    return template


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_permission("templates.delete"))]
)
async def delete_template(
    template_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete template.
    
    Args:
        template_id: Template ID
        session: Database session
        current_user: Current user
        
    Raises:
        HTTPException: If not found or has dependencies
    """
    service = ReportTemplateService(session)
    await service.delete_template(template_id, current_user.id)


@router.get(
    "/templates/{template_id}/history",
    response_model=List[ReportTemplateHistoryResponse],
    dependencies=[Depends(verify_permission("templates.view"))]
)
async def get_template_history(
    template_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ReportTemplateHistoryResponse]:
    """Get template history.
    
    Args:
        template_id: Template ID
        session: Database session
        current_user: Current user
        
    Returns:
        List of history records
        
    Raises:
        HTTPException: If not found
    """
    service = ReportTemplateService(session)
    history = await service.get_template_history(template_id)
    return history
