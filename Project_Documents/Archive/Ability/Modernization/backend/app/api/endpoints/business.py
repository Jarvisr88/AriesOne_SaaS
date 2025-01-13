from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, UUID4
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.core.logging import logger
from app.services.business import get_business_service
from app.db.session import get_db

router = APIRouter()

class ProcessRequest(BaseModel):
    """Process creation request"""
    process_type: str

class ProcessData(BaseModel):
    """Process data"""
    data: Dict

class ProcessResponse(BaseModel):
    """Process response"""
    process_id: str
    state: str
    errors: Optional[list[str]]
    result: Optional[Dict]

@router.post(
    "/process",
    response_model=ProcessResponse,
    summary="Create business process",
    description="Create new business process instance"
)
async def create_process(
    request: ProcessRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create business process with:
    1. Process type validation
    2. User authentication
    3. Process initialization
    4. State tracking
    """
    try:
        business_service = get_business_service(db)
        process = await business_service.create_process(
            request.process_type,
            current_user.id
        )
        
        state = await process.get_state()
        return ProcessResponse(
            process_id=state["process_id"],
            state=state["state"],
            errors=state.get("errors"),
            result=None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Process creation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Process creation failed"
        )

@router.post(
    "/process/{process_id}/validate",
    response_model=ProcessResponse,
    summary="Validate process data",
    description="Validate business process data"
)
async def validate_process(
    process_id: UUID4,
    data: ProcessData,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate process data with:
    1. Data validation
    2. Rule checking
    3. Error collection
    4. State update
    """
    try:
        business_service = get_business_service(db)
        process = await business_service.create_process(
            "claim_submission",  # TODO: Store process type
            current_user.id
        )
        process.process_id = process_id
        
        await process.validate(data.data)
        state = await process.get_state()
        
        return ProcessResponse(
            process_id=state["process_id"],
            state=state["state"],
            errors=state.get("errors"),
            result=None
        )
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Validation failed"
        )

@router.post(
    "/process/{process_id}/execute",
    response_model=ProcessResponse,
    summary="Execute business process",
    description="Execute business process with data"
)
async def execute_process(
    process_id: UUID4,
    data: ProcessData,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute process with:
    1. Data validation
    2. Business logic execution
    3. State management
    4. Result tracking
    """
    try:
        business_service = get_business_service(db)
        process = await business_service.create_process(
            "claim_submission",  # TODO: Store process type
            current_user.id
        )
        process.process_id = process_id
        
        result = await process.process(data.data)
        return ProcessResponse(
            process_id=result["process_id"],
            state=result["state"],
            errors=result.get("errors"),
            result={k: v for k, v in result.items() if k not in ["process_id", "state", "errors"]}
        )
    except Exception as e:
        logger.error(f"Execution error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Execution failed"
        )

@router.get(
    "/process/{process_id}",
    response_model=ProcessResponse,
    summary="Get process state",
    description="Get business process state"
)
async def get_process(
    process_id: UUID4,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get process state with:
    1. State retrieval
    2. Error checking
    3. Result collection
    4. Status tracking
    """
    try:
        business_service = get_business_service(db)
        process = await business_service.create_process(
            "claim_submission",  # TODO: Store process type
            current_user.id
        )
        process.process_id = process_id
        
        state = await process.get_state()
        return ProcessResponse(
            process_id=state["process_id"],
            state=state["state"],
            errors=state.get("errors"),
            result=None
        )
    except Exception as e:
        logger.error(f"State retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail="State retrieval failed"
        )

@router.get(
    "/process/metrics",
    summary="Get business metrics",
    description="Get business process metrics"
)
async def get_metrics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get business metrics:
    1. Processing times
    2. Validation times
    3. Error counts
    4. Success rates
    """
    try:
        business_service = get_business_service(db)
        return await business_service.get_metrics()
    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Metrics retrieval failed"
        )
