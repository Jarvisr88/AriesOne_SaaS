"""
FastAPI dependencies for image processing.
"""
from typing import Optional
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from redis import Redis
from .image_processor import ImageProcessor
from .config import settings


# Global instances
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

security = HTTPBearer()


async def get_image_processor() -> ImageProcessor:
    """Get or create ImageProcessor instance.
    
    Returns:
        ImageProcessor instance
    """
    return ImageProcessor(redis_client)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> int:
    """Verify JWT token and extract company ID.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        Company ID from token
        
    Raises:
        HTTPException: For invalid tokens
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        
        company_id = payload.get("company_id")
        if not company_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing company_id"
            )
            
        return company_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
