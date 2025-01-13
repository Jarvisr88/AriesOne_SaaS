# Database Module API Reference

## Core Components

### 1. Database Configuration
```python
from infrastructure.config import DatabaseSettings

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_SCHEMA: str = "public"
```

### 2. Database Connection
```python
from infrastructure.database import get_session

async with get_session() as session:
    result = await session.execute(query)
    await session.commit()
```

## Security API

### 1. Authentication
```python
from security.auth import DatabaseAuth

class DatabaseAuth:
    """Database authentication management."""
    
    async def create_role(
        self,
        role_name: str,
        permissions: List[str],
        description: Optional[str] = None
    ) -> Dict[str, Any]
    
    async def create_user(
        self,
        username: str,
        password: str,
        roles: List[str],
        connection_limit: int = 5
    ) -> Dict[str, Any]
    
    async def update_user_password(
        self,
        username: str,
        new_password: str
    ) -> Dict[str, Any]
    
    async def revoke_user_access(
        self,
        username: str,
        roles: Optional[List[str]] = None
    ) -> Dict[str, Any]
```

### 2. Encryption
```python
from security.encryption import DatabaseEncryption

class DatabaseEncryption:
    """Database encryption management."""
    
    async def setup_column_encryption(
        self,
        table_name: str,
        column_name: str
    ) -> Dict[str, Any]
    
    async def rotate_encryption_key(
        self,
        table_name: str,
        column_name: str
    ) -> Dict[str, Any]
    
    async def audit_encryption(
        self,
        table_name: Optional[str] = None
    ) -> Dict[str, Any]
```

### 3. Access Controls
```python
from security.access import DatabaseAccess

class DatabaseAccess:
    """Database access control management."""
    
    async def enable_row_level_security(
        self,
        table_name: str,
        policy_name: str,
        policy: str,
        roles: Optional[List[str]] = None
    ) -> Dict[str, Any]
    
    async def set_schema_permissions(
        self,
        schema_name: str,
        role: str,
        permissions: List[str]
    ) -> Dict[str, Any]
    
    async def transfer_ownership(
        self,
        object_type: str,
        object_name: str,
        new_owner: str
    ) -> Dict[str, Any]
```

## Management API

### 1. Health Checks
```python
from management.health import DatabaseHealth

async def check_connection_health() -> Dict[str, Any]
async def check_query_health() -> Dict[str, Any]
async def check_resource_health() -> Dict[str, Any]
```

### 2. Backup Management
```python
from management.backup import BackupManager

class BackupManager:
    """Database backup management."""
    
    async def create_backup(self) -> Dict[str, Any]
    async def restore_backup(self, filename: str) -> Dict[str, Any]
    async def verify_backup(self, filename: str) -> Dict[str, Any]
    async def cleanup_old_backups(self) -> Dict[str, Any]
```

### 3. Monitoring
```python
from management.monitor import DatabaseMonitor

class DatabaseMonitor:
    """Database monitoring management."""
    
    async def collect_table_metrics(self) -> Dict[str, Any]
    async def collect_performance_metrics(self) -> Dict[str, Any]
    async def collect_error_metrics(self) -> Dict[str, Any]
    async def collect_all_metrics(self) -> Dict[str, Any]
```

## Error Handling

All API methods return a dictionary with the following structure:
```python
{
    "status": str,  # "success" or "failure"
    "error": str,   # Error message if status is "failure"
    "timestamp": str,  # ISO format timestamp
    # Additional data specific to the operation
}
```

## Best Practices

1. **Connection Management**
```python
# Use context manager for sessions
async with get_session() as session:
    try:
        await session.execute(query)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

2. **Security**
```python
# Enable RLS for table
await access.enable_row_level_security(
    "patient_data",
    "org_policy",
    "org_id = current_setting('app.current_org')"
)

# Encrypt sensitive columns
await encryption.setup_column_encryption(
    "users",
    "ssn"
)
```

3. **Monitoring**
```python
# Regular health checks
health = await check_connection_health()
if health["status"] != "healthy":
    logger.error(f"Database unhealthy: {health['error']}")

# Collect metrics
metrics = await monitor.collect_all_metrics()
```

## Migration Management

```python
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback migration
alembic downgrade -1
```

## Examples

1. **User Management**
```python
# Create role and user
auth = DatabaseAuth()
await auth.create_role("app_user", ["SELECT", "INSERT"])
await auth.create_user("user1", "password", ["app_user"])
```

2. **Data Protection**
```python
# Setup encryption
encryption = DatabaseEncryption(master_key)
await encryption.setup_column_encryption("users", "ssn")
```

3. **Access Control**
```python
# Setup RLS
access = DatabaseAccess()
await access.enable_row_level_security(
    "patient_data",
    "org_policy",
    "org_id = current_setting('app.current_org')"
)
