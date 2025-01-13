# CmnResponse Modernization Deliverables

## 1. Models

### SQLAlchemy Models
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CmnResponseDB(Base):
    __tablename__ = "cmn_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    num_results = Column(Integer, nullable=True)
    carrier_number = Column(String(50), nullable=True)
    npi = Column(String(10), nullable=True, index=True)
    hic = Column(String(50), nullable=True, index=True)
    entries = relationship("CmnResponseEntryDB", back_populates="response")

class CmnResponseEntryDB(Base):
    __tablename__ = "cmn_response_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("cmn_responses.id"))
    response = relationship("CmnResponseDB", back_populates="entries")
```

### Pydantic Models
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class CmnResponseEntry(BaseModel):
    id: Optional[int]
    claim_number: str = Field(..., min_length=1, max_length=50)
    service_date: datetime
    
    class Config:
        orm_mode = True

class CmnResponse(BaseModel):
    id: Optional[int]
    num_results: Optional[int] = Field(None, ge=0)
    carrier_number: Optional[str] = Field(None, max_length=50)
    npi: Optional[str] = Field(None, regex=r'^\d{10}$')
    hic: Optional[str] = Field(None, max_length=50)
    entries: Optional[List[CmnResponseEntry]] = []
    
    class Config:
        orm_mode = True
        
    @validator('num_results')
    def validate_num_results(cls, v):
        if v is not None and v < 0:
            raise ValueError('Number of results cannot be negative')
        return v
```

## 2. API Endpoints

### FastAPI Routes
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .dependencies import get_db
from .models import CmnResponse, CmnResponseCreate
from .services import CmnResponseService

router = APIRouter(prefix="/api/v1/cmn", tags=["cmn"])

@router.post("/response", response_model=CmnResponse)
async def create_response(
    response: CmnResponseCreate,
    db: Session = Depends(get_db),
    service: CmnResponseService = Depends()
):
    return await service.create_response(db, response)

@router.get("/response/{response_id}", response_model=CmnResponse)
async def get_response(
    response_id: int,
    db: Session = Depends(get_db),
    service: CmnResponseService = Depends()
):
    return await service.get_response(db, response_id)
```

## 3. Services

### Business Logic
```python
from typing import Optional
from sqlalchemy.orm import Session
from .models import CmnResponse, CmnResponseDB
from .repositories import CmnResponseRepository

class CmnResponseService:
    def __init__(self, repository: CmnResponseRepository):
        self.repository = repository
    
    async def create_response(
        self,
        db: Session,
        response: CmnResponse
    ) -> CmnResponse:
        return await self.repository.create(db, response)
    
    async def get_response(
        self,
        db: Session,
        response_id: int
    ) -> Optional[CmnResponse]:
        return await self.repository.get(db, response_id)
```

## 4. Repositories

### Data Access Layer
```python
from sqlalchemy.orm import Session
from typing import Optional
from .models import CmnResponse, CmnResponseDB

class CmnResponseRepository:
    async def create(
        self,
        db: Session,
        response: CmnResponse
    ) -> CmnResponse:
        db_response = CmnResponseDB(**response.dict())
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return CmnResponse.from_orm(db_response)
    
    async def get(
        self,
        db: Session,
        response_id: int
    ) -> Optional[CmnResponse]:
        db_response = db.query(CmnResponseDB).filter(
            CmnResponseDB.id == response_id
        ).first()
        return CmnResponse.from_orm(db_response) if db_response else None
```

## 5. Utilities

### Helper Functions
```python
from typing import Dict, Any
import xml.etree.ElementTree as ET

def xml_to_dict(xml_str: str) -> Dict[str, Any]:
    """Convert XML to dictionary format."""
    root = ET.fromstring(xml_str)
    result = {}
    
    for child in root:
        result[child.tag] = child.text
        
    return result

def validate_npi(npi: str) -> bool:
    """Validate NPI format."""
    if not npi or not npi.isdigit() or len(npi) != 10:
        return False
    return True
```

## 6. Additional Deliverables

### Field Mappings
| C# Field | Python Field | Type | Notes |
|----------|--------------|------|-------|
| NumResults | num_results | Optional[int] | Must be >= 0 |
| CarrierNumber | carrier_number | Optional[str] | Max length 50 |
| Npi | npi | Optional[str] | 10 digits |
| Hic | hic | Optional[str] | Max length 50 |
| Entries | entries | List[CmnResponseEntry] | Collection |

### Transformation Rules
1. Field Names:
   - Convert PascalCase to snake_case
   - Maintain XML compatibility
   - Preserve field semantics

2. Data Types:
   - C# int? → Python Optional[int]
   - C# string → Python Optional[str]
   - C# List<T> → Python List[T]

3. Validation:
   - Add Pydantic validators
   - Implement type checking
   - Enforce constraints

4. XML Handling:
   - Preserve XML structure
   - Handle null values
   - Maintain attributes
