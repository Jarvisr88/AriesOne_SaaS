"""API router for image operations."""
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.imaging_models import (
    ImageResponse,
    ImageListResponse,
    ImageUploadRequest,
    MimeType,
    MimeTypeCreate
)
from ..services.imaging_service import ImageService, StorageClient
from ...Core.Modernization.dependencies import (
    get_session,
    get_current_user,
    get_storage_client
)


router = APIRouter(prefix="/images", tags=["Images"])


@router.post(
    "/{company}",
    response_model=ImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload image",
    description="Upload new image to storage"
)
async def upload_image(
    company: str = Path(..., description="Company identifier"),
    image: UploadFile = File(..., description="Image file"),
    metadata: ImageUploadRequest = Depends(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    storage: StorageClient = Depends(get_storage_client)
) -> ImageResponse:
    """Upload new image.
    
    Args:
        company: Company identifier
        image: Upload file
        metadata: Image metadata
        current_user: Authenticated user
        session: Database session
        storage: Storage client
        
    Returns:
        Image response with URL
        
    Raises:
        HTTPException: If upload fails
    """
    if not await has_company_access(current_user, company):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this company"
        )
    
    service = ImageService(session, storage)
    return await service.upload_image(company, image, metadata)


@router.get(
    "/{company}/{image_id}",
    response_model=ImageResponse,
    summary="Get image",
    description="Get image by ID"
)
async def get_image(
    company: str = Path(..., description="Company identifier"),
    image_id: str = Path(..., description="Image identifier"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    storage: StorageClient = Depends(get_storage_client)
) -> ImageResponse:
    """Get image by ID.
    
    Args:
        company: Company identifier
        image_id: Image identifier
        current_user: Authenticated user
        session: Database session
        storage: Storage client
        
    Returns:
        Image response with URL
        
    Raises:
        HTTPException: If image not found
    """
    if not await has_company_access(current_user, company):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this company"
        )
    
    service = ImageService(session, storage)
    return await service.get_image(company, image_id)


@router.delete(
    "/{company}/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete image",
    description="Delete image by ID"
)
async def delete_image(
    company: str = Path(..., description="Company identifier"),
    image_id: str = Path(..., description="Image identifier"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    storage: StorageClient = Depends(get_storage_client)
) -> None:
    """Delete image.
    
    Args:
        company: Company identifier
        image_id: Image identifier
        current_user: Authenticated user
        session: Database session
        storage: Storage client
        
    Raises:
        HTTPException: If image not found
    """
    if not await has_company_access(current_user, company):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this company"
        )
    
    service = ImageService(session, storage)
    await service.delete_image(company, image_id)


@router.get(
    "/{company}",
    response_model=ImageListResponse,
    summary="List images",
    description="List images for company"
)
async def list_images(
    company: str = Path(..., description="Company identifier"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    storage: StorageClient = Depends(get_storage_client)
) -> ImageListResponse:
    """List images for company.
    
    Args:
        company: Company identifier
        page: Page number
        page_size: Page size
        current_user: Authenticated user
        session: Database session
        storage: Storage client
        
    Returns:
        List of images with pagination
    """
    if not await has_company_access(current_user, company):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this company"
        )
    
    service = ImageService(session, storage)
    return await service.list_images(company, page, page_size)
