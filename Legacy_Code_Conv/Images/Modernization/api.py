"""
FastAPI endpoints for image processing.
"""
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    Security,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .image_processor import ImageProcessor
from .config import settings
from .schemas import ImageResponse, ImageMetadata
from .dependencies import get_image_processor, verify_token
import logging


router = APIRouter(prefix="/api/v1/images")
security = HTTPBearer()
logger = logging.getLogger(__name__)


@router.post(
    "/upload",
    response_model=ImageResponse,
    status_code=201,
    description="Upload and process an image"
)
async def upload_image(
    file: UploadFile = File(...),
    company_id: int = Depends(verify_token),
    processor: ImageProcessor = Depends(get_image_processor),
    token: HTTPAuthorizationCredentials = Security(security),
):
    """Upload and process an image.
    
    Args:
        file: Image file
        company_id: Company ID from token
        processor: Image processor instance
        token: JWT token
        
    Returns:
        Processed image metadata
        
    Raises:
        HTTPException: For invalid files or processing errors
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
            
        ext = file.filename.split('.')[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type"
            )
            
        # Process image
        result = await processor.process_upload(
            file,
            company_id,
            settings.MAX_IMAGE_SIZE,
            settings.JPEG_QUALITY
        )
        
        return ImageResponse(
            status="success",
            message="Image uploaded successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing image"
        )


@router.get(
    "/list",
    response_model=List[ImageMetadata],
    description="List company images"
)
async def list_images(
    company_id: int = Depends(verify_token),
    processor: ImageProcessor = Depends(get_image_processor),
    token: HTTPAuthorizationCredentials = Security(security),
):
    """List images for a company.
    
    Args:
        company_id: Company ID from token
        processor: Image processor instance
        token: JWT token
        
    Returns:
        List of image metadata
    """
    try:
        # List objects in S3 bucket
        response = await processor.s3.list_objects_v2(
            Bucket=settings.AWS_BUCKET_NAME,
            Prefix=f"companies/{company_id}/images/"
        )
        
        images = []
        for obj in response.get('Contents', []):
            # Get image hash from key
            image_hash = obj['Key'].split('/')[-1].split('.')[0]
            
            # Get cached metadata
            metadata = await processor._get_cached_image(image_hash)
            if metadata:
                images.append(metadata)
                
        return images
        
    except Exception as e:
        logger.error(f"Error listing images: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error listing images"
        )


@router.delete(
    "/{image_hash}",
    status_code=204,
    description="Delete an image"
)
async def delete_image(
    image_hash: str,
    company_id: int = Depends(verify_token),
    processor: ImageProcessor = Depends(get_image_processor),
    token: HTTPAuthorizationCredentials = Security(security),
):
    """Delete an image.
    
    Args:
        image_hash: Image hash
        company_id: Company ID from token
        processor: Image processor instance
        token: JWT token
    """
    try:
        await processor.delete_image(company_id, image_hash)
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error deleting image"
        )
