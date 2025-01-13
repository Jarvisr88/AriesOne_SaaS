"""Price utilities API router."""
from typing import Dict, List, Optional
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

from ..models.price_models import (
    PriceListCreate,
    PriceListResponse,
    PriceListUpdate,
    PriceItemCreate,
    PriceItemResponse,
    PriceItemUpdate,
    ICD9CodeCreate,
    ICD9CodeResponse,
    ICD9CodeUpdate,
    BulkUpdateRequest,
    BulkUpdateResponse,
    FileUploadResponse
)
from ..services.price_service import (
    PriceListService,
    PriceItemService,
    ICD9Service
)
from ...Core.Modernization.dependencies import (
    get_session,
    get_current_user
)


router = APIRouter()


# Price List endpoints
@router.get(
    "/price-lists",
    response_model=List[PriceListResponse],
    summary="Get price lists",
    description="Get all price lists"
)
async def get_price_lists(
    active_only: bool = Query(True, description="Only return active lists"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> List[PriceListResponse]:
    """Get all price lists.
    
    Args:
        active_only: Only return active lists
        current_user: Authenticated user
        session: Database session
        
    Returns:
        List of price lists
        
    Raises:
        HTTPException: If not authorized
    """
    if not current_user.has_permission('prices.view'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view price lists"
        )
    
    service = PriceListService(session)
    return await service.get_price_lists(active_only)


@router.post(
    "/price-lists",
    response_model=PriceListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create price list",
    description="Create new price list"
)
async def create_price_list(
    data: PriceListCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> PriceListResponse:
    """Create new price list.
    
    Args:
        data: Price list data
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Created price list
        
    Raises:
        HTTPException: If not authorized
    """
    if not current_user.has_permission('prices.create'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create price lists"
        )
    
    service = PriceListService(session)
    return await service.create_price_list(data, current_user.id)


@router.put(
    "/price-lists/{list_id}",
    response_model=PriceListResponse,
    summary="Update price list",
    description="Update existing price list"
)
async def update_price_list(
    list_id: int = Path(..., description="Price list ID"),
    data: PriceListUpdate = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> PriceListResponse:
    """Update price list.
    
    Args:
        list_id: Price list ID
        data: Update data
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Updated price list
        
    Raises:
        HTTPException: If not found or not authorized
    """
    if not current_user.has_permission('prices.update'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update price lists"
        )
    
    service = PriceListService(session)
    return await service.update_price_list(list_id, data, current_user.id)


# Price Item endpoints
@router.get(
    "/price-lists/{list_id}/items",
    response_model=List[PriceItemResponse],
    summary="Get price items",
    description="Get items in price list"
)
async def get_price_items(
    list_id: int = Path(..., description="Price list ID"),
    active_only: bool = Query(True, description="Only return active items"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> List[PriceItemResponse]:
    """Get price items.
    
    Args:
        list_id: Price list ID
        active_only: Only return active items
        current_user: Authenticated user
        session: Database session
        
    Returns:
        List of price items
        
    Raises:
        HTTPException: If not authorized
    """
    if not current_user.has_permission('prices.view'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view prices"
        )
    
    service = PriceItemService(session)
    return await service.get_items(list_id, active_only)


@router.post(
    "/price-lists/{list_id}/items",
    response_model=PriceItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create price item",
    description="Create new price item"
)
async def create_price_item(
    list_id: int = Path(..., description="Price list ID"),
    data: PriceItemCreate = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> PriceItemResponse:
    """Create price item.
    
    Args:
        list_id: Price list ID
        data: Item data
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Created item
        
    Raises:
        HTTPException: If not authorized
    """
    if not current_user.has_permission('prices.create'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create prices"
        )
    
    service = PriceItemService(session)
    return await service.create_item(data, current_user.id)


@router.put(
    "/price-lists/{list_id}/items/{item_id}",
    response_model=PriceItemResponse,
    summary="Update price item",
    description="Update existing price item"
)
async def update_price_item(
    list_id: int = Path(..., description="Price list ID"),
    item_id: int = Path(..., description="Item ID"),
    data: PriceItemUpdate = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> PriceItemResponse:
    """Update price item.
    
    Args:
        list_id: Price list ID
        item_id: Item ID
        data: Update data
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Updated item
        
    Raises:
        HTTPException: If not found or not authorized
    """
    if not current_user.has_permission('prices.update'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update prices"
        )
    
    service = PriceItemService(session)
    return await service.update_item(item_id, data, current_user.id)


@router.post(
    "/price-lists/{list_id}/bulk-update",
    response_model=BulkUpdateResponse,
    summary="Bulk update prices",
    description="Update multiple prices at once"
)
async def bulk_update_prices(
    list_id: int = Path(..., description="Price list ID"),
    data: BulkUpdateRequest = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> BulkUpdateResponse:
    """Bulk update prices.
    
    Args:
        list_id: Price list ID
        data: Update data
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Update results
        
    Raises:
        HTTPException: If not authorized
    """
    if not current_user.has_permission('prices.bulk_update'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for bulk updates"
        )
    
    service = PriceItemService(session)
    return await service.bulk_update(data, current_user.id)


@router.post(
    "/price-lists/{list_id}/upload",
    response_model=FileUploadResponse,
    summary="Upload price file",
    description="Upload and process price file"
)
async def upload_price_file(
    list_id: int = Path(..., description="Price list ID"),
    file: UploadFile = File(...),
    column_map: Dict[str, str] = Form(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> FileUploadResponse:
    """Upload price file.
    
    Args:
        list_id: Price list ID
        file: Uploaded file
        column_map: Column mapping
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Processing results
        
    Raises:
        HTTPException: If not authorized or file invalid
    """
    if not current_user.has_permission('prices.upload'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload files"
        )
    
    service = PriceItemService(session)
    return await service.process_file(file, column_map, current_user.id)


# ICD-9 endpoints
@router.get(
    "/icd9-codes",
    response_model=List[ICD9CodeResponse],
    summary="Get ICD-9 codes",
    description="Get all ICD-9 codes"
)
async def get_icd9_codes(
    active_only: bool = Query(True, description="Only return active codes"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> List[ICD9CodeResponse]:
    """Get ICD-9 codes.
    
    Args:
        active_only: Only return active codes
        current_user: Authenticated user
        session: Database session
        
    Returns:
        List of codes
        
    Raises:
        HTTPException: If not authorized
    """
    if not current_user.has_permission('icd9.view'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view ICD-9 codes"
        )
    
    service = ICD9Service(session)
    return await service.get_codes(active_only)


@router.post(
    "/icd9-codes",
    response_model=ICD9CodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create ICD-9 code",
    description="Create new ICD-9 code"
)
async def create_icd9_code(
    data: ICD9CodeCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> ICD9CodeResponse:
    """Create ICD-9 code.
    
    Args:
        data: Code data
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Created code
        
    Raises:
        HTTPException: If not authorized
    """
    if not current_user.has_permission('icd9.create'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create ICD-9 codes"
        )
    
    service = ICD9Service(session)
    return await service.create_code(data, current_user.id)


@router.put(
    "/icd9-codes/{code_id}",
    response_model=ICD9CodeResponse,
    summary="Update ICD-9 code",
    description="Update existing ICD-9 code"
)
async def update_icd9_code(
    code_id: int = Path(..., description="Code ID"),
    data: ICD9CodeUpdate = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> ICD9CodeResponse:
    """Update ICD-9 code.
    
    Args:
        code_id: Code ID
        data: Update data
        current_user: Authenticated user
        session: Database session
        
    Returns:
        Updated code
        
    Raises:
        HTTPException: If not found or not authorized
    """
    if not current_user.has_permission('icd9.update'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update ICD-9 codes"
        )
    
    service = ICD9Service(session)
    return await service.update_code(code_id, data, current_user.id)
