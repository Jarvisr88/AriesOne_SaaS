"""DMERC routes."""

from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

from ..dependencies import (
    get_dmerc_service,
    get_current_active_user
)
from ..schemas.dmerc import (
    DMERCFormCreate,
    DMERCFormUpdate,
    DMERCFormResponse,
    DMERCFormWithDetails,
    DMERCAttachmentResponse,
    DMERCHistoryResponse,
    DMERCStatusUpdate,
    DMERCSearchParams,
    DMERCSearchResponse
)
from ...services.dmerc_service import DMERCService
from ...domain.models.dmerc import (
    DMERCForm,
    DMERCFormType,
    DMERCStatus,
    DMERCAttachment,
    DMERCHistory
)
from ...domain.models.user import User

router = APIRouter(prefix="/dmerc", tags=["dmerc"])

@router.post("", response_model=DMERCFormResponse, status_code=status.HTTP_201_CREATED)
async def create_form(
    form: DMERCFormCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> DMERCForm:
    """Create new DMERC form."""
    return await dmerc_service.create_form(
        form.model_dump(),
        current_user.id
    )

@router.get("/{form_id}", response_model=DMERCFormWithDetails)
async def get_form(
    form_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> DMERCForm:
    """Get DMERC form by ID."""
    return await dmerc_service.get_by_id(form_id)

@router.patch("/{form_id}", response_model=DMERCFormResponse)
async def update_form(
    form_id: UUID,
    update: DMERCFormUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> DMERCForm:
    """Update DMERC form."""
    return await dmerc_service.update_form(
        form_id,
        update.model_dump(exclude_unset=True),
        current_user.id
    )

@router.post("/{form_id}/submit", response_model=DMERCFormResponse)
async def submit_form(
    form_id: UUID,
    update: DMERCStatusUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> DMERCForm:
    """Submit DMERC form."""
    return await dmerc_service.submit_form(
        form_id,
        current_user.id,
        update.notes
    )

@router.post("/{form_id}/approve", response_model=DMERCFormResponse)
async def approve_form(
    form_id: UUID,
    update: DMERCStatusUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> DMERCForm:
    """Approve DMERC form."""
    return await dmerc_service.approve_form(
        form_id,
        current_user.id,
        update.notes
    )

@router.post("/{form_id}/deny", response_model=DMERCFormResponse)
async def deny_form(
    form_id: UUID,
    update: DMERCStatusUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> DMERCForm:
    """Deny DMERC form."""
    if not update.notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Denial reason is required"
        )
    return await dmerc_service.deny_form(
        form_id,
        current_user.id,
        update.notes
    )

@router.post("/{form_id}/attachments", response_model=DMERCAttachmentResponse)
async def add_attachment(
    form_id: UUID,
    file: UploadFile = File(...),
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> DMERCAttachment:
    """Add attachment to DMERC form."""
    # TODO: Implement file upload handling
    file_path = f"uploads/{file.filename}"  # Placeholder
    
    return await dmerc_service.add_attachment(
        form_id,
        file.filename,
        file.content_type,
        0,  # TODO: Get actual file size
        file_path,
        current_user.id
    )

@router.get("/{form_id}/attachments", response_model=List[DMERCAttachmentResponse])
async def get_attachments(
    form_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> List[DMERCAttachment]:
    """Get DMERC form attachments."""
    return await dmerc_service.get_form_attachments(form_id)

@router.get("/{form_id}/history", response_model=List[DMERCHistoryResponse])
async def get_history(
    form_id: UUID,
    offset: int = 0,
    limit: int = 100,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> List[DMERCHistory]:
    """Get DMERC form history."""
    return await dmerc_service.get_form_history(
        form_id,
        offset=offset,
        limit=limit
    )

@router.post("/search", response_model=DMERCSearchResponse)
async def search_forms(
    params: DMERCSearchParams,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dmerc_service: Annotated[DMERCService, Depends(get_dmerc_service)]
) -> DMERCSearchResponse:
    """Search DMERC forms."""
    forms, total = await dmerc_service.search_forms(
        current_user.organization_id,  # TODO: Handle multiple organizations
        params.search_term,
        form_type=params.form_type,
        status=params.status,
        offset=params.offset,
        limit=params.limit
    )
    return DMERCSearchResponse(forms=forms, total=total)
