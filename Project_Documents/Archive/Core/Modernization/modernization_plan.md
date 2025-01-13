# Core Modernization Plan

## 1. Directory Structure

```
/Core
├── models/
│   ├── base.py
│   ├── form.py
│   ├── navigator.py
│   └── table_definitions.py
├── services/
│   ├── form_service.py
│   ├── navigation_service.py
│   └── validation_service.py
├── api/
│   ├── form_endpoints.py
│   ├── navigation_endpoints.py
│   └── validation_endpoints.py
├── repositories/
│   ├── base_repository.py
│   └── form_repository.py
└── utils/
    ├── validation.py
    └── state_management.py
```

## 2. Component Migration Plan

### Phase 1: Data Models

#### Base Models
```python
# models/base.py
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Optional[str] = Column(String(50))
    updated_by: Optional[str] = Column(String(50))
```

#### Form Models
```python
# models/form.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class FormState(BaseModel):
    is_dirty: bool = False
    is_new: bool = False
    is_deleted: bool = False
    validation_errors: Dict[str, List[str]] = Field(default_factory=dict)
    
class FormDefinition(BaseModel):
    id: str
    title: str
    components: List[Dict]
    validation_rules: Dict[str, Dict]
    permissions: Dict[str, List[str]]
```

### Phase 2: Services

#### Form Service
```python
# services/form_service.py
from typing import Optional, Dict
from fastapi import HTTPException
from .base_service import BaseService

class FormService(BaseService):
    async def create_form(self, definition: FormDefinition) -> str:
        """Create a new form definition"""
        
    async def get_form(self, form_id: str) -> Optional[FormDefinition]:
        """Retrieve form definition"""
        
    async def validate_form(self, form_id: str, data: Dict) -> Dict:
        """Validate form data"""
```

#### Navigation Service
```python
# services/navigation_service.py
from typing import List, Dict
from .base_service import BaseService

class NavigationService(BaseService):
    async def get_page(self, table: str, page: int, size: int) -> Dict:
        """Get paginated data"""
        
    async def search(self, table: str, query: str) -> List[Dict]:
        """Search records"""
        
    async def filter_data(self, table: str, filters: Dict) -> List[Dict]:
        """Apply filters to data"""
```

### Phase 3: API Endpoints

#### Form Endpoints
```python
# api/form_endpoints.py
from fastapi import APIRouter, Depends
from typing import Dict

router = APIRouter()

@router.post("/forms")
async def create_form(
    definition: FormDefinition,
    service: FormService = Depends(get_form_service)
) -> Dict:
    """Create new form definition"""
    
@router.get("/forms/{form_id}")
async def get_form(
    form_id: str,
    service: FormService = Depends(get_form_service)
) -> FormDefinition:
    """Get form definition"""
```

#### Navigation Endpoints
```python
# api/navigation_endpoints.py
from fastapi import APIRouter, Depends
from typing import Dict, List

router = APIRouter()

@router.get("/data/{table}")
async def get_data(
    table: str,
    page: int = 1,
    size: int = 50,
    service: NavigationService = Depends(get_navigation_service)
) -> Dict:
    """Get paginated data"""
```

### Phase 4: Frontend Components

#### Form Component
```typescript
// components/Form.tsx
interface FormProps {
  definition: FormDefinition;
  onSubmit: (data: any) => Promise<void>;
  onValidate: (data: any) => Promise<ValidationResult>;
}

const Form: React.FC<FormProps> = ({ definition, onSubmit, onValidate }) => {
  // Implementation
};
```

#### Navigation Grid
```typescript
// components/DataGrid.tsx
interface DataGridProps {
  data: any[];
  columns: ColumnDefinition[];
  onPageChange: (page: number) => void;
  onFilter: (filters: FilterDefinition) => void;
}

const DataGrid: React.FC<DataGridProps> = ({ data, columns, onPageChange, onFilter }) => {
  // Implementation
};
```

## 3. Migration Steps

1. **Database Migration**
   - Create SQLAlchemy models
   - Set up Alembic migrations
   - Create data migration scripts
   - Validate data integrity

2. **Backend Implementation**
   - Set up FastAPI application
   - Implement services
   - Create API endpoints
   - Add validation logic

3. **Frontend Development**
   - Create React components
   - Implement state management
   - Add form validation
   - Create navigation system

4. **Integration**
   - Connect frontend to API
   - Implement authentication
   - Add error handling
   - Set up logging

## 4. Testing Strategy

1. **Unit Tests**
   - Test individual components
   - Validate business logic
   - Check error handling
   - Verify data transformations

2. **Integration Tests**
   - Test API endpoints
   - Verify database operations
   - Check component integration
   - Validate workflows

3. **End-to-End Tests**
   - Test complete workflows
   - Verify user interactions
   - Check data consistency
   - Validate performance

## 5. Deployment Plan

1. **Preparation**
   - Set up deployment pipeline
   - Create staging environment
   - Prepare rollback procedures
   - Document deployment steps

2. **Database Migration**
   - Back up existing data
   - Run migration scripts
   - Validate migrated data
   - Test database performance

3. **Application Deployment**
   - Deploy backend services
   - Deploy frontend application
   - Configure environment
   - Set up monitoring

4. **Validation**
   - Test deployed application
   - Verify functionality
   - Check performance
   - Monitor errors

## 6. Timeline

1. **Week 1-2: Foundation**
   - Set up project structure
   - Create base models
   - Implement core services
   - Set up testing framework

2. **Week 3-4: Core Features**
   - Implement form system
   - Create navigation components
   - Add validation logic
   - Set up state management

3. **Week 5-6: Integration**
   - Connect components
   - Implement workflows
   - Add error handling
   - Create documentation

4. **Week 7-8: Testing & Deployment**
   - Run comprehensive tests
   - Fix identified issues
   - Deploy to staging
   - Prepare for production

## 7. Success Criteria

1. **Functionality**
   - All core features working
   - Data integrity maintained
   - Performance requirements met
   - User workflows preserved

2. **Quality**
   - Test coverage > 80%
   - No critical bugs
   - Performance benchmarks met
   - Code quality standards met

3. **User Experience**
   - Intuitive interface
   - Responsive design
   - Clear error messages
   - Efficient workflows
