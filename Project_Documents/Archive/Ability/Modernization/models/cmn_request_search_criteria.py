from pydantic import BaseModel
from typing import Optional

class CmnRequestSearchCriteria(BaseModel):
    npi: Optional[str]
    hic: Optional[str]
    hcpcs: Optional[str]
    mbi: Optional[str]
    max_results: Optional[int]

    class Config:
        orm_mode = True
