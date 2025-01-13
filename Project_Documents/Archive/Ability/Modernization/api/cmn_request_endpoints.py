from fastapi import APIRouter, HTTPException, Depends
from models.cmn_request import CmnRequest
from services.cmn_request_service import process_cmn_request

router = APIRouter()

@router.post("/cmn_request")
async def create_cmn_request(request: CmnRequest):
    try:
        result = process_cmn_request(request)
        return {"message": "CmnRequest processed successfully", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
