from fastapi import APIRouter, HTTPException
from models.cmn_response import CmnResponse

router = APIRouter()

@router.post("/cmn_response")
async def create_cmn_response(response: CmnResponse):
    try:
        # Process the response
        return {"message": "CmnResponse processed successfully", "data": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
