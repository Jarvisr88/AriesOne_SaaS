"""Properties API router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...Core.Modernization.api.dependencies import (
    get_current_user,
    get_session
)
from ...Core.Modernization.models.user import User
from ..models.properties_models import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourceHistoryResponse,
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    SettingHistoryResponse,
    CultureUpdate
)
from ..services.properties_service import (
    ResourceService,
    SettingService
)


router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get("/resources", response_model=List[ResourceResponse])
async def get_resources(
    culture: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[ResourceResponse]:
    """Get all resources.
    
    Args:
        culture: Culture code
        session: Database session
        current_user: Current user
        
    Returns:
        List of resources
    """
    service = ResourceService(session)
    return await service.get_resources(culture)


@router.get("/resources/{name}", response_model=ResourceResponse)
async def get_resource(
    name: str,
    culture: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> ResourceResponse:
    """Get resource by name.
    
    Args:
        name: Resource name
        culture: Culture code
        session: Database session
        current_user: Current user
        
    Returns:
        Resource
        
    Raises:
        HTTPException: If not found
    """
    service = ResourceService(session)
    resource = await service.get_resource(name, culture)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return resource


@router.post("/resources", response_model=ResourceResponse)
async def create_resource(
    data: ResourceCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> ResourceResponse:
    """Create resource.
    
    Args:
        data: Resource data
        session: Database session
        current_user: Current user
        
    Returns:
        Created resource
    """
    service = ResourceService(session)
    return await service.create_resource(data, current_user.id)


@router.put("/resources/{name}", response_model=ResourceResponse)
async def update_resource(
    name: str,
    data: ResourceUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> ResourceResponse:
    """Update resource.
    
    Args:
        name: Resource name
        data: Update data
        session: Database session
        current_user: Current user
        
    Returns:
        Updated resource
    """
    service = ResourceService(session)
    return await service.update_resource(name, data, current_user.id)


@router.get(
    "/resources/{name}/history",
    response_model=List[ResourceHistoryResponse]
)
async def get_resource_history(
    name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[ResourceHistoryResponse]:
    """Get resource history.
    
    Args:
        name: Resource name
        session: Database session
        current_user: Current user
        
    Returns:
        List of history records
    """
    service = ResourceService(session)
    return await service.get_resource_history(name)


@router.get("/settings", response_model=List[SettingResponse])
async def get_settings(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[SettingResponse]:
    """Get all settings.
    
    Args:
        session: Database session
        current_user: Current user
        
    Returns:
        List of settings
    """
    service = SettingService(session)
    return await service.get_settings()


@router.get("/settings/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> SettingResponse:
    """Get setting by key.
    
    Args:
        key: Setting key
        session: Database session
        current_user: Current user
        
    Returns:
        Setting
        
    Raises:
        HTTPException: If not found
    """
    service = SettingService(session)
    setting = await service.get_setting(key)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    return setting


@router.post("/settings", response_model=SettingResponse)
async def create_setting(
    data: SettingCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> SettingResponse:
    """Create setting.
    
    Args:
        data: Setting data
        session: Database session
        current_user: Current user
        
    Returns:
        Created setting
    """
    service = SettingService(session)
    return await service.create_setting(data, current_user.id)


@router.put("/settings/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    data: SettingUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> SettingResponse:
    """Update setting.
    
    Args:
        key: Setting key
        data: Update data
        session: Database session
        current_user: Current user
        
    Returns:
        Updated setting
    """
    service = SettingService(session)
    return await service.update_setting(key, data, current_user.id)


@router.get(
    "/settings/{key}/history",
    response_model=List[SettingHistoryResponse]
)
async def get_setting_history(
    key: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[SettingHistoryResponse]:
    """Get setting history.
    
    Args:
        key: Setting key
        session: Database session
        current_user: Current user
        
    Returns:
        List of history records
    """
    service = SettingService(session)
    return await service.get_setting_history(key)
