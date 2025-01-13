from fastapi import APIRouter, HTTPException, Depends
from models.cmn_request_search_criteria import CmnRequestSearchCriteria
from services.cmn_request_search_criteria_service import process_cmn_request_search_criteria

router = APIRouter()

@router.post("/cmn_request_search_criteria")
async def create_cmn_request_search_criteria(criteria: CmnRequestSearchCriteria):
    try:
        result = process_cmn_request_search_criteria(criteria)
        return {"message": "CmnRequestSearchCriteria processed successfully", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
