# AriesOne SaaS Development Guide

## Development Environment

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- RabbitMQ 3.8+
- Docker & Docker Compose
- Git

### Setup
```bash
# Clone repository
git clone https://github.com/your-org/ariesone-saas.git
cd ariesone-saas

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Copy environment file
cp .env.example .env

# Start development services
docker-compose up -d

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

## Code Organization

### Directory Structure
```
ariesone_saas/
├── app/
│   ├── api/              # API endpoints
│   │   ├── v1/
│   │   └── deps.py
│   ├── core/             # Core configuration
│   │   ├── config.py
│   │   └── security.py
│   ├── models/           # Database models
│   │   ├── user.py
│   │   └── price.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py
│   │   └── price.py
│   ├── services/         # Business logic
│   │   ├── user.py
│   │   └── price.py
│   └── utils/            # Utility functions
├── tests/                # Test suite
│   ├── api/
│   ├── services/
│   └── conftest.py
├── alembic/              # Database migrations
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

## Coding Standards

### Python Style Guide
- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Use double quotes for strings
- Sort imports using isort

### Example Code Style
```python
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    email: EmailStr
    password: str
    name: str
    role: Optional[str] = "user"
    
    class Config:
        """Pydantic configuration."""
        
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "name": "John Doe",
                "role": "admin"
            }
        }
```

### Documentation
- Use docstrings for modules, classes, and functions
- Follow Google style docstrings
- Include type hints
- Document exceptions
- Provide usage examples

### Example Documentation
```python
def calculate_price(
    base_price: float,
    discount: Optional[float] = None,
    tax_rate: float = 0.1
) -> float:
    """Calculate final price including discount and tax.
    
    Args:
        base_price: Base price of the item
        discount: Optional discount percentage (0-1)
        tax_rate: Tax rate percentage (0-1)
    
    Returns:
        float: Final price after discount and tax
    
    Raises:
        ValueError: If discount or tax_rate is not between 0 and 1
    
    Example:
        >>> calculate_price(100.0, 0.1, 0.2)
        108.0
    """
    if discount and not 0 <= discount <= 1:
        raise ValueError("Discount must be between 0 and 1")
    
    if not 0 <= tax_rate <= 1:
        raise ValueError("Tax rate must be between 0 and 1")
    
    discounted_price = (
        base_price * (1 - discount)
        if discount
        else base_price
    )
    
    return discounted_price * (1 + tax_rate)
```

## Testing

### Test Structure
```python
import pytest
from app.services.price import calculate_price


def test_calculate_price_with_discount():
    """Test price calculation with discount."""
    result = calculate_price(100.0, 0.1, 0.2)
    assert result == pytest.approx(108.0)


def test_calculate_price_without_discount():
    """Test price calculation without discount."""
    result = calculate_price(100.0, tax_rate=0.2)
    assert result == pytest.approx(120.0)


def test_calculate_price_invalid_discount():
    """Test price calculation with invalid discount."""
    with pytest.raises(ValueError):
        calculate_price(100.0, 1.5)
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/services/test_price.py

# Run specific test function
pytest tests/services/test_price.py::test_calculate_price_with_discount
```

## Development Workflow

### Feature Development
1. Create feature branch
   ```bash
   git checkout -b feature/new-feature
   ```

2. Write tests
   ```bash
   touch tests/services/test_new_feature.py
   ```

3. Implement feature
   ```bash
   touch app/services/new_feature.py
   ```

4. Run tests and linting
   ```bash
   pytest
   flake8
   black .
   isort .
   ```

5. Commit changes
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. Push branch
   ```bash
   git push origin feature/new-feature
   ```

7. Create pull request

### Code Review Process
1. Automated checks
   - Test coverage
   - Code style
   - Type checking
   - Security scanning

2. Manual review
   - Code correctness
   - Performance
   - Security
   - Documentation

3. Review feedback
   - Address comments
   - Update code
   - Re-run checks

4. Merge approval
   - Squash and merge
   - Delete branch

## Debugging

### Logging
```python
import structlog

logger = structlog.get_logger(__name__)

def process_order(order_id: str) -> None:
    """Process an order."""
    logger.info("processing_order", order_id=order_id)
    try:
        # Process order
        logger.info("order_processed", order_id=order_id)
    except Exception as e:
        logger.error(
            "order_processing_failed",
            order_id=order_id,
            error=str(e)
        )
        raise
```

### Debugging Tools
- pdb/ipdb for interactive debugging
- logging for tracing
- pytest for debugging tests
- FastAPI debug mode

## Performance

### Database
- Use appropriate indexes
- Optimize queries
- Use connection pooling
- Implement caching
- Monitor query performance

### Caching
- Cache expensive operations
- Use appropriate cache keys
- Set proper TTL
- Handle cache invalidation
- Monitor cache hit rates

### Async Operations
- Use async/await
- Handle background tasks
- Implement retry logic
- Monitor task queues
- Handle failures gracefully

## Security

### Authentication
- Use secure password hashing
- Implement token-based auth
- Handle session management
- Support MFA
- Monitor auth failures

### Authorization
- Implement RBAC
- Check permissions
- Validate input
- Sanitize output
- Log access attempts

### Data Protection
- Use HTTPS
- Encrypt sensitive data
- Implement rate limiting
- Handle CORS
- Monitor security events
