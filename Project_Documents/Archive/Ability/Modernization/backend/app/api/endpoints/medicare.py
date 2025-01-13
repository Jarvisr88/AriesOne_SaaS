from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import date

from app.models.medicare import (
    Beneficiary,
    Claim,
    ServiceCode,
    ClaimStatus,
    MainframeResponse,
)
from app.services.mainframe_client import (
    MainframeClient,
    MainframeConnectionError,
    MainframeTimeoutError,
    MainframeDataError,
)
from app.core.dependencies import get_current_user, RateLimiter
from app.core.logging import logger

router = APIRouter()
rate_limiter = RateLimiter(requests_per_minute=60)

@router.get(
    "/beneficiary/{medicare_id}",
    response_model=Beneficiary,
    summary="Get beneficiary information",
    response_description="Returns detailed beneficiary information",
)
async def get_beneficiary(
    medicare_id: str,
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Retrieve beneficiary information from Medicare mainframe.
    
    Parameters:
    - medicare_id: Medicare Beneficiary Identifier (MBI)
    
    Returns:
    - Beneficiary information including coverage details
    """
    try:
        async with MainframeClient() as client:
            response = await client.get_beneficiary(medicare_id)
            
        if not response.success:
            raise HTTPException(
                status_code=404,
                detail=f"Beneficiary not found: {response.error.message}",
            )
            
        return response.data
        
    except MainframeConnectionError as e:
        logger.error(f"Mainframe connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Medicare service temporarily unavailable",
        )
    except MainframeTimeoutError as e:
        logger.error(f"Mainframe timeout error: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out",
        )
    except MainframeDataError as e:
        logger.error(f"Data processing error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail="Invalid data received from Medicare service",
        )

@router.get(
    "/claim/{claim_id}",
    response_model=Claim,
    summary="Get claim information",
    response_description="Returns detailed claim information",
)
async def get_claim(
    claim_id: str,
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Retrieve claim information from Medicare mainframe.
    
    Parameters:
    - claim_id: Unique claim identifier
    
    Returns:
    - Claim information including line items and status
    """
    try:
        async with MainframeClient() as client:
            response = await client.get_claim(claim_id)
            
        if not response.success:
            raise HTTPException(
                status_code=404,
                detail=f"Claim not found: {response.error.message}",
            )
            
        return response.data
        
    except MainframeConnectionError as e:
        logger.error(f"Mainframe connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Medicare service temporarily unavailable",
        )
    except MainframeTimeoutError as e:
        logger.error(f"Mainframe timeout error: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out",
        )
    except MainframeDataError as e:
        logger.error(f"Data processing error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail="Invalid data received from Medicare service",
        )

@router.post(
    "/claim",
    response_model=Claim,
    status_code=201,
    summary="Submit new claim",
    response_description="Returns created claim information",
)
async def submit_claim(
    claim: Claim,
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Submit a new claim to Medicare mainframe.
    
    Parameters:
    - claim: Claim information including beneficiary, service, and payment details
    
    Returns:
    - Created claim information with assigned claim ID
    """
    try:
        async with MainframeClient() as client:
            response = await client.submit_claim(claim.dict())
            
        if not response.success:
            raise HTTPException(
                status_code=400,
                detail=f"Claim submission failed: {response.error.message}",
            )
            
        return response.data
        
    except MainframeConnectionError as e:
        logger.error(f"Mainframe connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Medicare service temporarily unavailable",
        )
    except MainframeTimeoutError as e:
        logger.error(f"Mainframe timeout error: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out",
        )
    except MainframeDataError as e:
        logger.error(f"Data processing error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail="Invalid data received from Medicare service",
        )

@router.get(
    "/service-codes",
    response_model=List[ServiceCode],
    summary="Get service codes",
    response_description="Returns list of available service codes",
)
async def get_service_codes(
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
    active_only: bool = Query(True, description="Filter only active service codes"),
):
    """
    Retrieve list of Medicare service codes.
    
    Parameters:
    - active_only: Filter only active service codes (default: True)
    
    Returns:
    - List of service codes with descriptions and fee schedules
    """
    try:
        async with MainframeClient() as client:
            response = await client.get_service_codes()
            
        if not response.success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to retrieve service codes: {response.error.message}",
            )
            
        codes = response.data
        if active_only:
            codes = [code for code in codes if code.get("active", True)]
            
        return codes
        
    except MainframeConnectionError as e:
        logger.error(f"Mainframe connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Medicare service temporarily unavailable",
        )
    except MainframeTimeoutError as e:
        logger.error(f"Mainframe timeout error: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out",
        )
    except MainframeDataError as e:
        logger.error(f"Data processing error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail="Invalid data received from Medicare service",
        )

@router.get(
    "/eligibility/{medicare_id}/{service_code}",
    response_model=dict,
    summary="Check service eligibility",
    response_description="Returns eligibility information for specified service",
)
async def check_eligibility(
    medicare_id: str,
    service_code: str,
    service_date: date = Query(None, description="Date of service"),
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Check beneficiary eligibility for specific service.
    
    Parameters:
    - medicare_id: Medicare Beneficiary Identifier (MBI)
    - service_code: Service procedure code
    - service_date: Date of service (optional, defaults to current date)
    
    Returns:
    - Eligibility information including coverage and payment details
    """
    try:
        async with MainframeClient() as client:
            response = await client.check_eligibility(medicare_id, service_code)
            
        if not response.success:
            raise HTTPException(
                status_code=400,
                detail=f"Eligibility check failed: {response.error.message}",
            )
            
        return response.data
        
    except MainframeConnectionError as e:
        logger.error(f"Mainframe connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Medicare service temporarily unavailable",
        )
    except MainframeTimeoutError as e:
        logger.error(f"Mainframe timeout error: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out",
        )
    except MainframeDataError as e:
        logger.error(f"Data processing error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail="Invalid data received from Medicare service",
        )

@router.get(
    "/claim/{claim_id}/status",
    response_model=ClaimStatus,
    summary="Get claim status",
    response_description="Returns current claim processing status",
)
async def get_claim_status(
    claim_id: str,
    current_user = Depends(get_current_user),
    _rate_limit = Depends(rate_limiter),
):
    """
    Retrieve current status of a claim.
    
    Parameters:
    - claim_id: Unique claim identifier
    
    Returns:
    - Current claim processing status
    """
    try:
        async with MainframeClient() as client:
            response = await client.get_claim_status(claim_id)
            
        if not response.success:
            raise HTTPException(
                status_code=404,
                detail=f"Claim status not found: {response.error.message}",
            )
            
        return response.data.get("status")
        
    except MainframeConnectionError as e:
        logger.error(f"Mainframe connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Medicare service temporarily unavailable",
        )
    except MainframeTimeoutError as e:
        logger.error(f"Mainframe timeout error: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out",
        )
    except MainframeDataError as e:
        logger.error(f"Data processing error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail="Invalid data received from Medicare service",
        )
