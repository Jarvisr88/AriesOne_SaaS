from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from app.core.deps import get_current_user
from app.services.forms import FormService
from app.schemas.forms import (
    FormTemplate,
    FormSubmission,
    FormProgress,
    FormError,
    FormCreate,
    FormUpdate,
    FormSubmit
)
from app.core.logging import logger
from app.core.analytics import analytics

router = APIRouter()

@router.post("/templates/", response_model=FormTemplate)
async def create_template(
    template: FormCreate,
    current_user = Depends(get_current_user)
):
    """Create new form template"""
    try:
        form_service = FormService(current_user)
        result = await form_service.create_template(
            name=template.name,
            type=template.type,
            fields=template.fields
        )
        analytics.track_template_creation(result.id)
        return result
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates/{template_id}", response_model=FormTemplate)
async def get_template(
    template_id: str,
    current_user = Depends(get_current_user)
):
    """Get form template by ID"""
    try:
        form_service = FormService(current_user)
        template = await form_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        analytics.track_template_view(template.id)
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/templates/{template_id}", response_model=FormTemplate)
async def update_template(
    template_id: str,
    template: FormUpdate,
    current_user = Depends(get_current_user)
):
    """Update form template"""
    try:
        form_service = FormService(current_user)
        result = await form_service.update_template(
            id=template_id,
            name=template.name,
            fields=template.fields
        )
        analytics.track_template_update(result.id)
        return result
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/submit/", response_model=FormSubmission)
async def submit_form(
    data: str = Form(...),
    files: List[UploadFile] = File(None),
    current_user = Depends(get_current_user)
):
    """Submit form with files"""
    try:
        form_service = FormService(current_user)
        result = await form_service.submit_form(
            template_id=data.template_id,
            data=data.data,
            files=files
        )
        analytics.track_form_submission(result.id)
        return result
    except Exception as e:
        logger.error(f"Error submitting form: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/submissions/{submission_id}", response_model=FormSubmission)
async def get_submission(
    submission_id: str,
    current_user = Depends(get_current_user)
):
    """Get form submission by ID"""
    try:
        form_service = FormService(current_user)
        submission = await form_service.get_submission(submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        analytics.track_submission_view(submission.id)
        return submission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/submissions/{submission_id}/progress")
async def track_progress(
    submission_id: str,
    current_user = Depends(get_current_user)
):
    """Track form submission progress with Server-Sent Events"""
    try:
        form_service = FormService(current_user)
        
        async def event_generator():
            async for progress in form_service.track_progress(submission_id):
                analytics.track_progress_update(submission_id)
                yield {
                    "event": "progress",
                    "data": progress.json(),
                    "retry": 1000
                }
        
        return EventSourceResponse(event_generator())
    except Exception as e:
        logger.error(f"Error tracking progress: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/submissions/{submission_id}/download")
async def download_submission(
    submission_id: str,
    current_user = Depends(get_current_user)
):
    """Download form submission data"""
    try:
        form_service = FormService(current_user)
        
        async def file_generator():
            async for chunk in form_service.get_submission_file(submission_id):
                yield chunk
        
        analytics.track_submission_download(submission_id)
        return StreamingResponse(
            file_generator(),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=submission_{submission_id}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error downloading submission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analytics/submissions")
async def get_submission_analytics(
    template_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get form submission analytics"""
    try:
        form_service = FormService(current_user)
        return await form_service.get_submission_analytics(
            template_id,
            start_date,
            end_date
        )
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
