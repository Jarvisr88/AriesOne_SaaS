# AriesOne SaaS Developer Guide

Version: 1.0.0
Last Updated: 2025-01-10

## Development Environment

### 1. Setup

#### Prerequisites
```bash
# Required software
python >= 3.8
node >= 16
postgresql >= 13
redis >= 6
docker >= 20
kubernetes >= 1.20
```

#### Installation
```bash
# Clone repository
git clone https://github.com/ariesone/saas.git
cd saas

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm install

# Setup database
createdb ariesone_dev
alembic upgrade head

# Start development server
python manage.py runserver
```

### 2. Configuration

#### Environment Variables
```bash
# Core settings
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your_secret_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/ariesone_dev
REDIS_URL=redis://localhost:6379/0

# Services
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

## Code Structure

### 1. Backend Architecture

#### Core Modules
```
core/
├── auth/           # Authentication
├── tenants/        # Multi-tenancy
├── inventory/      # Inventory management
├── orders/         # Order processing
├── billing/        # Billing and invoicing
└── analytics/      # Reporting and analytics
```

#### Service Layer
```python
from core.services import BaseService

class InventoryService(BaseService):
    async def create_item(self, data: dict) -> dict:
        """Create inventory item."""
        async with self.db.transaction():
            item = await self.db.inventory.create(**data)
            await self.events.emit('inventory.created', item)
            return item
            
    async def update_stock(self, item_id: str, quantity: int) -> dict:
        """Update item stock level."""
        async with self.db.transaction():
            item = await self.db.inventory.get(item_id)
            if not item:
                raise NotFoundError('Item not found')
                
            updated = await item.update(quantity=quantity)
            await self.events.emit('inventory.updated', updated)
            return updated
```

### 2. Frontend Architecture

#### Component Structure
```
src/
├── components/     # Reusable components
├── pages/         # Route components
├── hooks/         # Custom hooks
├── services/      # API clients
├── store/         # State management
└── utils/         # Helper functions
```

#### Component Example
```typescript
import React from 'react';
import { useInventory } from '@/hooks/inventory';
import { InventoryTable, SearchBar } from '@/components';

export const InventoryPage: React.FC = () => {
    const { items, loading, error } = useInventory();
    const [search, setSearch] = useState('');
    
    const filteredItems = useMemo(() => {
        return items.filter(item => 
            item.name.toLowerCase().includes(search.toLowerCase())
        );
    }, [items, search]);
    
    return (
        <div className="p-4">
            <SearchBar value={search} onChange={setSearch} />
            <InventoryTable 
                items={filteredItems}
                loading={loading}
                error={error}
            />
        </div>
    );
};
```

## API Development

### 1. Endpoint Structure

#### REST Endpoints
```python
from fastapi import APIRouter, Depends
from core.auth import get_current_user
from core.schemas import InventoryItem

router = APIRouter()

@router.get('/inventory')
async def list_inventory(
    current_user = Depends(get_current_user),
    page: int = 1,
    per_page: int = 20
):
    """List inventory items."""
    items = await inventory_service.list(
        tenant_id=current_user.tenant_id,
        page=page,
        per_page=per_page
    )
    return items

@router.post('/inventory')
async def create_inventory(
    item: InventoryItem,
    current_user = Depends(get_current_user)
):
    """Create inventory item."""
    created = await inventory_service.create(
        tenant_id=current_user.tenant_id,
        **item.dict()
    )
    return created
```

### 2. Data Validation

#### Schema Validation
```python
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class InventoryItem(BaseModel):
    id: Optional[str]
    sku: str
    name: str
    description: Optional[str]
    quantity: int
    minimum_quantity: int
    maximum_quantity: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('quantity must be positive')
        return v
        
    @validator('maximum_quantity')
    def maximum_must_exceed_minimum(cls, v, values):
        if v and v < values['minimum_quantity']:
            raise ValueError('maximum must exceed minimum')
        return v
```

## Testing

### 1. Unit Tests

#### Test Example
```python
import pytest
from unittest.mock import Mock
from core.services import InventoryService

@pytest.fixture
def inventory_service():
    db = Mock()
    events = Mock()
    return InventoryService(db=db, events=events)

async def test_create_item(inventory_service):
    # Arrange
    data = {
        'sku': 'TEST-001',
        'name': 'Test Item',
        'quantity': 10
    }
    inventory_service.db.inventory.create.return_value = {
        **data,
        'id': '123'
    }
    
    # Act
    result = await inventory_service.create_item(data)
    
    # Assert
    assert result['sku'] == data['sku']
    assert result['name'] == data['name']
    inventory_service.events.emit.assert_called_once()
```

### 2. Integration Tests

#### Test Setup
```python
import pytest
from httpx import AsyncClient
from core.app import create_app
from core.db import Database

@pytest.fixture
async def app():
    app = create_app()
    async with Database.connect() as db:
        app.state.db = db
        yield app

@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client

async def test_list_inventory(client, auth_headers):
    # Arrange
    await seed_test_data()
    
    # Act
    response = await client.get(
        '/api/inventory',
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data['items']) > 0
```

## Security

### 1. Authentication

#### JWT Implementation
```python
from jose import jwt
from datetime import datetime, timedelta
from core.config import settings

def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        **data,
        'exp': expire,
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def verify_token(token: str) -> dict:
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.JWTError:
        raise InvalidTokenError()
```

### 2. Authorization

#### Role-Based Access
```python
from functools import wraps
from core.auth import get_current_user
from core.errors import PermissionDenied

def requires_permission(permission: str):
    """Permission decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = await get_current_user()
            if not user.has_permission(permission):
                raise PermissionDenied()
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@router.post('/inventory')
@requires_permission('inventory.create')
async def create_inventory(item: InventoryItem):
    """Create inventory item."""
    return await inventory_service.create(item)
```

## Error Handling

### 1. Custom Exceptions

#### Exception Classes
```python
class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or 'INTERNAL_ERROR'
        super().__init__(message)

class NotFoundError(AppError):
    """Resource not found."""
    def __init__(self, message: str = 'Resource not found'):
        super().__init__(message, 'NOT_FOUND')

class ValidationError(AppError):
    """Data validation error."""
    def __init__(self, message: str, errors: dict = None):
        super().__init__(message, 'VALIDATION_ERROR')
        self.errors = errors or {}
```

### 2. Error Middleware

#### Error Handler
```python
from fastapi import Request
from fastapi.responses import JSONResponse
from core.errors import AppError

async def error_handler(request: Request, exc: Exception):
    """Global error handler."""
    if isinstance(exc, AppError):
        return JSONResponse(
            status_code=400,
            content={
                'error': {
                    'code': exc.code,
                    'message': exc.message,
                    'details': getattr(exc, 'errors', None)
                }
            }
        )
    
    # Log unexpected errors
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred'
            }
        }
    )
```

## Performance

### 1. Caching

#### Cache Implementation
```python
from functools import wraps
from core.cache import redis_cache

def cache_response(ttl: int = 300):
    """Cache decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Try cache first
            cached = await redis_cache.get(key)
            if cached:
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await redis_cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

@router.get('/inventory/{item_id}')
@cache_response(ttl=300)
async def get_inventory(item_id: str):
    """Get inventory item."""
    return await inventory_service.get(item_id)
```

### 2. Query Optimization

#### Database Queries
```python
from sqlalchemy import select
from core.models import Inventory

async def list_inventory(tenant_id: str, page: int = 1, per_page: int = 20):
    """Optimized inventory query."""
    query = (
        select(Inventory)
        .where(Inventory.tenant_id == tenant_id)
        .order_by(Inventory.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .options(
            selectinload(Inventory.location),
            selectinload(Inventory.category)
        )
    )
    
    return await database.fetch_all(query)
```

## Deployment

### 1. Docker Setup

#### Dockerfile
```dockerfile
FROM python:3.8-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Kubernetes

#### Deployment Config
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ariesone-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ariesone-api
  template:
    metadata:
      labels:
        app: ariesone-api
    spec:
      containers:
      - name: api
        image: ariesone/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ariesone-secrets
              key: database-url
```

## Monitoring

### 1. Logging

#### Logger Setup
```python
import logging
import structlog
from core.config import settings

def setup_logging():
    """Configure structured logging."""
    logging.basicConfig(level=settings.LOG_LEVEL)
    
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
```

### 2. Metrics

#### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram
from fastapi import FastAPI
from starlette_prometheus import PrometheusMiddleware

app = FastAPI()
app.add_middleware(PrometheusMiddleware)

# Custom metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_latency = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)
```

## Support

For development support:
- GitHub: github.com/ariesone/saas
- Documentation: docs.ariesone.com/dev
- Email: dev-support@ariesone.com

## Changelog

### 1.0.0 (2025-01-10)
- Initial release
- Core functionality
- API documentation
- Developer tools
