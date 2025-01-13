"""
Same or Similar Claims API Module
This module provides REST endpoints for checking same or similar claims.
Modernized from C# Windows Forms implementation.
"""
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, File
from fastapi.security import HTTPBearer
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import cryptography.x509 as x509
from ..services.same_or_similar_service import SameOrSimilarService
from ..models.cmn_request_model import CmnRequest
from ..models.cmn_response_model import CmnResponse
from ..dependencies import get_same_or_similar_service

router = APIRouter(prefix="/api/v1/same-or-similar", tags=["same-or-similar"])
security = HTTPBearer()

class SameOrSimilarRequest(BaseModel):
    """Request model for same/similar claim check"""
    npi: str = Field(..., description="Provider NPI")
    billing_code: str = Field(..., description="Billing code to check")
    policy_number: str = Field(..., description="Policy number")

class NPIEntry(BaseModel):
    """NPI information model"""
    npi: str = Field(..., description="NPI number")
    state: str = Field(..., description="State code")
    description: str = Field(..., description="Location description")

@router.get("/npis")
async def get_npis(
    service: SameOrSimilarService = Depends(get_same_or_similar_service)
) -> List[NPIEntry]:
    """
    Get available NPIs.
    
    Args:
        service (SameOrSimilarService): Service instance
        
    Returns:
        List[NPIEntry]: Available NPIs
    """
    try:
        return await service.get_npis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/billing-codes")
async def get_billing_codes(
    service: SameOrSimilarService = Depends(get_same_or_similar_service)
) -> List[str]:
    """
    Get available billing codes.
    
    Args:
        service (SameOrSimilarService): Service instance
        
    Returns:
        List[str]: Available billing codes
    """
    try:
        return await service.get_billing_codes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check")
async def check_same_or_similar(
    request: SameOrSimilarRequest,
    certificate: UploadFile = File(...),
    service: SameOrSimilarService = Depends(get_same_or_similar_service)
) -> Dict[str, Any]:
    """
    Check for same or similar claims.
    
    Args:
        request (SameOrSimilarRequest): Check request
        certificate (UploadFile): X.509 certificate file
        service (SameOrSimilarService): Service instance
        
    Returns:
        Dict[str, Any]: Check results
        
    Raises:
        HTTPException: If check fails
    """
    try:
        # Read and validate certificate
        cert_data = await certificate.read()
        cert = x509.load_pem_x509_certificate(cert_data)
        
        # Perform check
        response = await service.check_same_or_similar(
            request.npi,
            request.billing_code,
            request.policy_number,
            cert
        )
        
        return {
            "success": True,
            "claims": response.claims if response else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings")
async def get_settings(
    service: SameOrSimilarService = Depends(get_same_or_similar_service)
) -> Dict[str, Any]:
    """
    Get integration settings.
    
    Args:
        service (SameOrSimilarService): Service instance
        
    Returns:
        Dict[str, Any]: Current settings
    """
    try:
        return await service.get_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
