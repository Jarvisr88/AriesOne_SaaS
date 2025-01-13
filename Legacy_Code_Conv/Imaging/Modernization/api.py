"""
FastAPI endpoints for the imaging service.
"""
from typing import Dict, Any, List, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    Security,
    BackgroundTasks,
)
from fastapi.security import HTTPBearer
import logging
import json
from .security import SecurityManager
from .storage import StorageManager
from .cache import CacheManager
from .processor import ImageProcessor
from .background import BackgroundManager
from .schemas import (
    ImageUploadResponse,
    ImageMetadata,
    ImageListResponse,
    ErrorResponse,
)
from .config import settings
from .ai_service import AIService
from .search_service import SearchService
from .analytics_service import AnalyticsService
from .monitoring_service import MonitoringService
from .maintenance_service import MaintenanceService
import io
import asyncio
import aiohttp
from datetime import datetime


# Initialize router
router = APIRouter(prefix=settings.API_V1_PREFIX)
logger = logging.getLogger(__name__)

# Initialize managers
security_manager = SecurityManager()
storage_manager = StorageManager()
cache_manager = CacheManager()
processor_manager = ImageProcessor()
background_manager = BackgroundManager()
ai_service = AIService()
search_service = SearchService()
analytics_service = AnalyticsService()
monitoring_service = MonitoringService()
maintenance_service = MaintenanceService()

# Start background services
@router.on_event("startup")
async def startup_event():
    """Start background services."""
    try:
        # Start monitoring
        await monitoring_service.start_monitoring()
        
        # Start maintenance
        await maintenance_service.start_maintenance()
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")


@router.post(
    "/images/upload",
    response_model=ImageUploadResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["images"],
    summary="Upload image",
    description="Upload and process a new image"
)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: Dict[str, Any] = Depends(security_manager.get_current_user)
) -> ImageUploadResponse:
    """Upload and process an image."""
    try:
        # Validate company access
        company_id = user.get("company_id")
        if not company_id:
            raise HTTPException(
                status_code=400,
                detail="Company ID not found in token"
            )
            
        # Read file data
        file_data = await file.read()
        
        # Track upload start
        await analytics_service.track_upload(
            company_id,
            "upload_started",
            {"filename": file.filename},
            "started"
        )
        
        # Validate image
        await processor_manager.validate_image(io.BytesIO(file_data))
        
        # Generate secure filename
        image_id = security_manager.generate_secure_filename(
            file.filename,
            company_id
        )
        
        # Prepare metadata
        metadata = {
            "original_filename": file.filename,
            "content_type": file.content_type,
            "uploaded_by": user.get("sub", "unknown"),
            "company_id": str(company_id)
        }
        
        # Upload original
        result = await storage_manager.upload_image(
            company_id,
            image_id,
            io.BytesIO(file_data),
            file.content_type,
            metadata
        )
        
        # Analyze image
        analysis = await ai_service.analyze_image(file_data)
        
        # Index for search
        await search_service.index_image(
            company_id,
            image_id,
            metadata,
            analysis
        )
        
        # Schedule background processing
        background_tasks.add_task(
            background_manager.process_image_async,
            company_id,
            image_id,
            file_data,
            file.content_type,
            {**metadata, **analysis}
        )
        
        # Track successful upload
        await analytics_service.track_upload(
            company_id,
            image_id,
            metadata,
            "success"
        )
        
        return ImageUploadResponse(
            status="success",
            message="Image uploaded successfully",
            data={**result, "analysis": analysis}
        )
        
    except Exception as e:
        # Track failed upload
        if company_id:
            await analytics_service.track_upload(
                company_id,
                "upload_failed",
                {"error": str(e)},
                "failed"
            )
            
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/images/{image_id}",
    response_model=ImageMetadata,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["images"],
    summary="Get image",
    description="Get image details and URLs"
)
async def get_image(
    image_id: str,
    user: Dict[str, Any] = Depends(security_manager.get_current_user)
) -> ImageMetadata:
    """Get image details.
    
    Args:
        image_id: Image identifier
        user: Current user from token
        
    Returns:
        Image metadata
        
    Raises:
        HTTPException: If image not found or access denied
    """
    try:
        # Validate company access
        company_id = user.get("company_id")
        if not company_id:
            raise HTTPException(
                status_code=400,
                detail="Company ID not found in token"
            )
            
        # Try cache first
        cached = await cache_manager.get(f"{company_id}/{image_id}")
        if cached:
            return ImageMetadata(**cached)
            
        # Get from storage
        result = await storage_manager.get_image(company_id, image_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Image not found"
            )
            
        # Cache result
        await cache_manager.set(
            f"{company_id}/{image_id}",
            result
        )
            
        return ImageMetadata(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.delete(
    "/images/{image_id}",
    status_code=204,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["images"],
    summary="Delete image",
    description="Delete an image"
)
async def delete_image(
    image_id: str,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(security_manager.get_current_user)
) -> None:
    """Delete an image.
    
    Args:
        image_id: Image identifier
        background_tasks: Background task manager
        user: Current user from token
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        # Validate company access
        company_id = user.get("company_id")
        if not company_id:
            raise HTTPException(
                status_code=400,
                detail="Company ID not found in token"
            )
            
        # Delete image
        success = await storage_manager.delete_image(
            company_id,
            image_id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Image not found"
            )
            
        # Clear cache in background
        background_tasks.add_task(
            cache_manager.invalidate_pattern,
            f"{company_id}/{image_id}*"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/images",
    response_model=ImageListResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["images"],
    summary="List images",
    description="List company images"
)
async def list_images(
    user: Dict[str, Any] = Depends(security_manager.get_current_user)
) -> ImageListResponse:
    """List company images.
    
    Args:
        user: Current user from token
        
    Returns:
        List of image metadata
        
    Raises:
        HTTPException: If listing fails
    """
    try:
        # Validate company access
        company_id = user.get("company_id")
        if not company_id:
            raise HTTPException(
                status_code=400,
                detail="Company ID not found in token"
            )
            
        # Try cache first
        cache_key = f"list:{company_id}"
        cached = await cache_manager.get(cache_key)
        if cached:
            return ImageListResponse(**cached)
            
        # List images
        images = await storage_manager.list_images(company_id)
        
        response = ImageListResponse(
            status="success",
            message=f"Found {len(images)} images",
            data=images
        )
        
        # Cache result
        await cache_manager.set(
            cache_key,
            response.dict(),
            ttl=300  # 5 minutes
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error listing images: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/images/search",
    response_model=ImageListResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["images"],
    summary="Search images",
    description="Search for images using text query and filters"
)
async def search_images(
    query: str,
    filters: Optional[str] = None,
    sort: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    user: Dict[str, Any] = Depends(security_manager.get_current_user)
) -> ImageListResponse:
    """Search for images.
    
    Args:
        query: Search query
        filters: JSON-encoded filters
        sort: Sort field and order (field:order)
        page: Page number
        size: Page size
        user: Current user
        
    Returns:
        Search results
    """
    try:
        # Validate company access
        company_id = user.get("company_id")
        if not company_id:
            raise HTTPException(
                status_code=400,
                detail="Company ID not found in token"
            )
            
        # Parse filters
        filter_dict = json.loads(filters) if filters else None
        
        # Execute search
        results = await search_service.search_images(
            company_id,
            query,
            filter_dict,
            sort,
            page,
            size
        )
        
        return ImageListResponse(
            status="success",
            message=f"Found {results['total']} images",
            data=results['hits']
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/images/stats",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["images"],
    summary="Get usage statistics",
    description="Get image usage statistics"
)
async def get_stats(
    days: int = 30,
    user: Dict[str, Any] = Depends(security_manager.get_current_user)
) -> Dict[str, Any]:
    """Get usage statistics.
    
    Args:
        days: Time period in days
        user: Current user
        
    Returns:
        Usage statistics
    """
    try:
        # Validate company access
        company_id = user.get("company_id")
        if not company_id:
            raise HTTPException(
                status_code=400,
                detail="Company ID not found in token"
            )
            
        # Get statistics
        stats = await analytics_service.get_usage_stats(
            company_id,
            days
        )
        
        return {
            "status": "success",
            "message": "Statistics retrieved successfully",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/health",
    tags=["system"],
    summary="Health check",
    description="Check system health"
)
async def health_check() -> Dict[str, Any]:
    """Check system health.
    
    Returns:
        Health status
    """
    try:
        # Check dependencies
        results = await asyncio.gather(
            storage_manager.check_health(),
            cache_manager.check_health(),
            search_service.check_health(),
            return_exceptions=True
        )
        
        # Process results
        services = {
            "storage": "healthy",
            "cache": "healthy",
            "search": "healthy"
        }
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                services[
                    list(services.keys())[i]
                ] = "unhealthy"
                
        # Overall status
        status = (
            "healthy"
            if all(s == "healthy" for s in services.values())
            else "degraded"
        )
        
        return {
            "status": status,
            "services": services,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get(
    "/metrics",
    tags=["system"],
    summary="System metrics",
    description="Get system metrics"
)
async def get_metrics() -> Dict[str, Any]:
    """Get system metrics.
    
    Returns:
        System metrics
    """
    try:
        # Get metrics from Prometheus
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.PROMETHEUS_API}/api/v1/query",
                params={
                    "query": 'job="imaging_service"'
                }
            ) as response:
                if response.status != 200:
                    raise Exception(
                        f"Metric query failed: {await response.text()}"
                    )
                    
                data = await response.json()
                
        return {
            "status": "success",
            "data": data["data"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post(
    "/maintenance/cleanup",
    tags=["system"],
    summary="Run cleanup",
    description="Run system cleanup"
)
async def run_cleanup(
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(
        security_manager.get_admin_user
    )
) -> Dict[str, Any]:
    """Run system cleanup.
    
    Args:
        background_tasks: Background task manager
        user: Admin user
        
    Returns:
        Cleanup status
    """
    try:
        # Schedule cleanup
        background_tasks.add_task(
            maintenance_service._cleanup_old_data
        )
        
        return {
            "status": "success",
            "message": "Cleanup scheduled",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post(
    "/maintenance/optimize",
    tags=["system"],
    summary="Run optimization",
    description="Run system optimization"
)
async def run_optimization(
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(
        security_manager.get_admin_user
    )
) -> Dict[str, Any]:
    """Run system optimization.
    
    Args:
        background_tasks: Background task manager
        user: Admin user
        
    Returns:
        Optimization status
    """
    try:
        # Schedule optimization
        background_tasks.add_task(
            maintenance_service._optimize_indexes
        )
        
        return {
            "status": "success",
            "message": "Optimization scheduled",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
