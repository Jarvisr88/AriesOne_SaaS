from pydantic import BaseModel
from typing import Optional

class CmnRequestSearchCriteria(BaseModel):
    npi: Optional[str]
    hic: Optional[str]
    hcpcs: Optional[str]
    mbi: Optional[str]
    max_results: Optional[int]

class CmnRequest(BaseModel):
    medicare_mainframe: Optional['MedicareMainframe']
    search_criteria: Optional[CmnRequestSearchCriteria]
    mock_response: Optional[bool]

    class Config:
        orm_mode = True
