from fastapi import APIRouter, HTTPException
from models.cmn_response_entry import CmnResponseEntry

router = APIRouter()

@router.post("/cmn_response_entry")
async def create_cmn_response_entry(entry: CmnResponseEntry):
    try:
        # Process the entry
        return {"message": "CmnResponseEntry processed successfully", "data": entry}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
