from pydantic import BaseModel
from typing import Optional

class CmnResponseEntry(BaseModel):
    submitted_hcpcs: Optional[str]
    approved_hcpcs: Optional[str]
    initial_date: Optional[str]
    status_code: Optional[str]
    status_description: Optional[str]
    status_date: Optional[str]
    length_of_need: Optional[str]

    class Config:
        orm_mode = True
