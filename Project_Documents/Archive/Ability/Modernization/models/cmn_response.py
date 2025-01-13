from pydantic import BaseModel
from typing import Optional, List

class CmnResponseEntry(BaseModel):
    # Define fields for CmnResponseEntry
    pass

class CmnResponse(BaseModel):
    num_results: Optional[int]
    carrier_number: Optional[str]
    npi: Optional[str]
    hic: Optional[str]
    claims: Optional[List[CmnResponseEntry]]

    class Config:
        orm_mode = True
