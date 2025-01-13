# Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Connection Issues

#### Symptoms
- API returns 500 error with database connection message
- Alembic migrations fail
- Slow query performance

#### Solutions

1. **Check Database Connection**
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
psql -h localhost -U user -d ariesone
```

2. **Connection Pool Issues**
```python
# Check pool settings in config.py
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30

# Monitor active connections
SELECT count(*) FROM pg_stat_activity;
```

3. **Migration Issues**
```bash
# Reset migrations
alembic downgrade base

# Recreate migrations
alembic revision --autogenerate -m "reset"
alembic upgrade head
```

### 2. Authentication Problems

#### Symptoms
- JWT token validation fails
- Unauthorized access errors
- Token expiration issues

#### Solutions

1. **Invalid Token**
```python
# Check token format
import jwt

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            "your-secret-key",
            algorithms=["HS256"]
        )
    except jwt.InvalidTokenError as e:
        print(f"Token error: {str(e)}")
        return None
```

2. **Token Expiration**
```python
# Verify token expiration
from datetime import datetime, timezone

def is_token_expired(token: str) -> bool:
    payload = decode_token(token)
    if not payload:
        return True
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    return datetime.now(timezone.utc) >= exp
```

3. **Missing Permissions**
```python
# Check user roles
async def verify_permissions(user_id: str, required_role: str):
    user = await get_user(user_id)
    if required_role not in user.roles:
        raise PermissionError(f"Missing role: {required_role}")
```

### 3. Cache Issues

#### Symptoms
- Slow API response times
- Inconsistent data
- High memory usage

#### Solutions

1. **Redis Connection**
```bash
# Check Redis status
redis-cli ping

# Monitor Redis
redis-cli monitor

# Clear cache
redis-cli flushall
```

2. **Cache Invalidation**
```python
# Implement cache versioning
async def get_cached_data(key: str, version: int = 1):
    versioned_key = f"{key}:v{version}"
    data = await redis.get(versioned_key)
    if not data:
        data = await fetch_fresh_data()
        await redis.set(versioned_key, data)
    return data
```

3. **Memory Issues**
```bash
# Check Redis memory usage
redis-cli info memory

# Set memory limit
redis-cli config set maxmemory 2gb
redis-cli config set maxmemory-policy allkeys-lru
```

### 4. Performance Issues

#### Symptoms
- Slow API response times
- High CPU/memory usage
- Database timeouts

#### Solutions

1. **Query Optimization**
```python
# Add indexes
async def optimize_queries():
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_company_npi 
        ON companies(npi);
        
        CREATE INDEX IF NOT EXISTS idx_company_active 
        ON companies(is_active) 
        WHERE is_active = true;
    """)
```

2. **N+1 Query Problem**
```python
# Use join instead of separate queries
async def get_company_with_locations(company_id: str):
    query = select(Company, Location).join(
        Location,
        Company.id == Location.company_id
    ).where(Company.id == company_id)
    return await db.execute(query)
```

3. **Caching Strategy**
```python
# Implement caching layers
async def get_company(company_id: str):
    # Try cache first
    cached = await cache.get(f"company:{company_id}")
    if cached:
        return cached
        
    # Database fallback
    company = await db.fetch_one(
        "SELECT * FROM companies WHERE id = $1",
        company_id
    )
    
    # Cache result
    await cache.set(
        f"company:{company_id}",
        company,
        expire=3600
    )
    
    return company
```

### 5. API Error Handling

#### Symptoms
- Unclear error messages
- Missing error details
- Inconsistent error formats

#### Solutions

1. **Custom Error Handler**
```python
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

async def error_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": str(exc.detail),
                "path": request.url.path
            }
        }
    )
```

2. **Error Logging**
```python
import logging

logger = logging.getLogger(__name__)

async def log_error(error: Exception, context: dict):
    logger.error(
        "Error occurred",
        extra={
            "error": str(error),
            "type": error.__class__.__name__,
            "context": context
        }
    )
```

3. **Validation Errors**
```python
from pydantic import ValidationError

def handle_validation_error(error: ValidationError) -> dict:
    return {
        "error": {
            "code": 422,
            "message": "Validation Error",
            "details": [
                {
                    "field": e["loc"][0],
                    "message": e["msg"]
                }
                for e in error.errors()
            ]
        }
    }
```

## Monitoring and Debugging

### 1. Logging Setup
```python
import logging
import json
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
```

### 2. Metrics Collection
```python
from prometheus_client import Counter, Histogram

# Request metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Latency metrics
request_latency = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)
```

### 3. Health Checks
```python
async def check_health() -> dict:
    return {
        "status": "healthy",
        "checks": {
            "database": await check_db(),
            "cache": await check_redis(),
            "queue": await check_rabbitmq()
        },
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Support Resources

### 1. Logging Analysis
- Use [Kibana](https://www.elastic.co/kibana) for log visualization
- Set up log alerts in [Grafana](https://grafana.com)
- Use [Sentry](https://sentry.io) for error tracking

### 2. Performance Monitoring
- Monitor metrics with [Prometheus](https://prometheus.io)
- Use [pgHero](https://pghero.doximity.com) for PostgreSQL insights
- Profile code with [cProfile](https://docs.python.org/3/library/profile.html)

### 3. Documentation
- API docs: http://localhost:8000/docs
- Architecture docs: /docs/architecture
- Source code: https://github.com/ariesone/saas
