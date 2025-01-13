# Performance Optimization Guidelines

## Overview
This document outlines performance optimization strategies and best practices for the Ability module in the AriesOne SaaS platform.

## Database Optimization

### 1. Query Optimization
```sql
-- Use covering indexes for frequently accessed queries
CREATE INDEX idx_applications_company_status ON applications (company_id, status);
CREATE INDEX idx_workflows_company_type ON workflows (company_id, workflow_type);

-- Use partial indexes for filtered queries
CREATE INDEX idx_active_applications ON applications (id)
WHERE status = 'active' AND is_deleted = false;

-- Use composite indexes for sorted queries
CREATE INDEX idx_applications_created ON applications (company_id, created_at DESC);
```

### 2. Connection Pooling
```python
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True
)
```

### 3. Batch Operations
```python
async def bulk_insert_applications(
    applications: List[ApplicationCreate],
    chunk_size: int = 1000
):
    """Insert applications in chunks."""
    for i in range(0, len(applications), chunk_size):
        chunk = applications[i:i + chunk_size]
        await session.execute(
            insert(Application),
            [app.dict() for app in chunk]
        )
        await session.commit()
```

## Caching Strategy

### 1. Multi-Level Caching
```python
class CachingStrategy:
    def __init__(self):
        self.local_cache = LRUCache(1000)  # Memory cache
        self.redis_cache = RedisCache()     # Distributed cache
    
    async def get_application(self, app_id: int):
        # Try local cache
        app = self.local_cache.get(app_id)
        if app:
            return app
            
        # Try Redis cache
        app = await self.redis_cache.get(app_id)
        if app:
            self.local_cache.set(app_id, app)
            return app
            
        # Get from database
        app = await db.get_application(app_id)
        if app:
            await self.redis_cache.set(app_id, app)
            self.local_cache.set(app_id, app)
        return app
```

### 2. Cache Invalidation
```python
async def invalidate_application_cache(app_id: int):
    """Smart cache invalidation."""
    # Get related cache keys
    keys = await cache.get_related_keys(f"app:{app_id}")
    
    # Batch delete
    await cache.delete_many(keys)
    
    # Publish invalidation event
    await event_bus.publish(
        "cache.invalidate",
        {
            "type": "application",
            "id": app_id,
            "timestamp": datetime.utcnow()
        }
    )
```

## API Optimization

### 1. Response Compression
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000  # Only compress responses > 1KB
)
```

### 2. Request Validation
```python
class ApplicationFilter(BaseModel):
    """Optimized filter model."""
    company_id: int
    status: Optional[List[ApplicationStatus]]
    created_after: Optional[datetime]
    created_before: Optional[datetime]
    
    @validator("status")
    def validate_status_list(cls, v):
        """Limit status list size."""
        if v and len(v) > 10:
            raise ValueError("Too many status values")
        return v
    
    @validator("created_after")
    def validate_date_range(cls, v, values):
        """Limit date range."""
        if (
            v and
            values.get("created_before") and
            (values["created_before"] - v).days > 90
        ):
            raise ValueError("Date range too large")
        return v
```

## Background Processing

### 1. Task Queue Configuration
```python
from celery import Celery
from celery.schedules import crontab

celery = Celery(
    "ability",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2"
)

celery.conf.update(
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True
)
```

### 2. Batch Processing
```python
@celery.task
def process_applications_batch(
    app_ids: List[int],
    action: str,
    metadata: Dict
):
    """Process applications in parallel."""
    chunk_size = 100
    results = []
    
    for i in range(0, len(app_ids), chunk_size):
        chunk = app_ids[i:i + chunk_size]
        tasks = [
            process_single_application.s(
                app_id,
                action,
                metadata
            )
            for app_id in chunk
        ]
        job = group(tasks)
        results.extend(job.apply_async())
    
    return results
```

## Memory Management

### 1. Resource Limits
```python
import resource

def set_memory_limit(max_gb: int = 4):
    """Set memory limit for process."""
    max_bytes = max_gb * 1024 * 1024 * 1024  # Convert GB to bytes
    resource.setrlimit(
        resource.RLIMIT_AS,
        (max_bytes, max_bytes)
    )
```

### 2. Object Pooling
```python
from queue import Queue
from typing import TypeVar, Generic

T = TypeVar('T')

class ObjectPool(Generic[T]):
    """Generic object pool."""
    def __init__(
        self,
        factory,
        initial_size: int = 10,
        max_size: int = 100
    ):
        self.factory = factory
        self.max_size = max_size
        self.pool = Queue(max_size)
        
        # Pre-populate pool
        for _ in range(initial_size):
            self.pool.put(factory())
    
    def acquire(self) -> T:
        """Get object from pool."""
        try:
            return self.pool.get_nowait()
        except Empty:
            if self.pool.qsize() < self.max_size:
                return self.factory()
            return self.pool.get()
    
    def release(self, obj: T):
        """Return object to pool."""
        try:
            self.pool.put_nowait(obj)
        except Full:
            pass  # Pool is full, discard object
```

## Monitoring and Profiling

### 1. Performance Metrics
```python
from prometheus_client import Counter, Histogram

REQUEST_LATENCY = Histogram(
    "application_request_latency_seconds",
    "Application request latency",
    ["method", "endpoint"]
)

REQUEST_COUNT = Counter(
    "application_request_count",
    "Application request count",
    ["method", "endpoint", "status"]
)

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Monitor request performance."""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response
```

### 2. Query Profiling
```python
from sqlalchemy import event
from time import time

def setup_query_profiling(engine):
    """Setup query profiling."""
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany
    ):
        conn.info.setdefault("query_start_time", []).append(time())

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany
    ):
        total = time() - conn.info["query_start_time"].pop()
        if total > 0.1:  # Log slow queries (>100ms)
            logger.warning(
                "Slow query detected: %s, duration: %.2fs",
                statement,
                total
            )
```

## Load Testing

### 1. Load Test Configuration
```python
from locust import HttpUser, task, between

class ApplicationUser(HttpUser):
    """Simulated application user."""
    wait_time = between(1, 5)
    
    @task(3)
    def view_applications(self):
        """View applications list."""
        self.client.get(
            "/applications",
            params={
                "company_id": self.company_id,
                "status": "active"
            }
        )
    
    @task(1)
    def create_application(self):
        """Create new application."""
        self.client.post(
            "/applications",
            json={
                "title": "Load Test Application",
                "company_id": self.company_id,
                "workflow_id": self.workflow_id
            }
        )
```

### 2. Performance Benchmarks
```python
import asyncio
import statistics
from typing import List

async def run_performance_benchmark(
    endpoint: str,
    requests: int = 1000,
    concurrency: int = 10
):
    """Run performance benchmark."""
    async with aiohttp.ClientSession() as session:
        latencies: List[float] = []
        
        async def make_request():
            start = time.time()
            async with session.get(endpoint) as response:
                await response.text()
                latencies.append(time.time() - start)
        
        # Create task groups
        tasks = []
        for _ in range(requests):
            if len(tasks) >= concurrency:
                await asyncio.gather(*tasks)
                tasks = []
            tasks.append(asyncio.create_task(make_request()))
        
        if tasks:
            await asyncio.gather(*tasks)
        
        return {
            "requests": requests,
            "concurrency": concurrency,
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "avg_latency": statistics.mean(latencies),
            "p95_latency": statistics.quantiles(latencies, n=20)[18],
            "p99_latency": statistics.quantiles(latencies, n=100)[98]
        }
```

## Implementation Checklist

1. Database Optimization
   - [ ] Review and optimize existing queries
   - [ ] Implement connection pooling
   - [ ] Add necessary indexes
   - [ ] Set up batch operations

2. Caching Strategy
   - [ ] Implement multi-level caching
   - [ ] Set up cache invalidation
   - [ ] Configure cache timeouts
   - [ ] Add cache warming

3. API Optimization
   - [ ] Enable response compression
   - [ ] Implement request validation
   - [ ] Add pagination
   - [ ] Optimize payload size

4. Background Processing
   - [ ] Configure task queues
   - [ ] Implement batch processing
   - [ ] Set up retry policies
   - [ ] Add monitoring

5. Memory Management
   - [ ] Set resource limits
   - [ ] Implement object pooling
   - [ ] Add memory monitoring
   - [ ] Configure garbage collection

6. Monitoring and Profiling
   - [ ] Set up performance metrics
   - [ ] Configure query profiling
   - [ ] Add logging
   - [ ] Create dashboards

7. Load Testing
   - [ ] Create test scenarios
   - [ ] Set up benchmarking
   - [ ] Define performance SLAs
   - [ ] Automate testing
