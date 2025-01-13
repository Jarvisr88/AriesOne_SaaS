# Database Module Setup Guide

## Overview
This guide covers the setup and configuration of the AriesOne Database module, including PostgreSQL configuration, connection management, security settings, and monitoring tools.

## Prerequisites
- Python 3.8+
- PostgreSQL 15.0+
- Docker (optional)

## Installation

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Environment Configuration**
Create a `.env` file with the following settings:
```env
# Database Connection
POSTGRES_USER=ariesone
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ariesone
POSTGRES_SCHEMA=public

# Connection Pool
POOL_SIZE=20
MAX_OVERFLOW=10
POOL_TIMEOUT=30
POOL_RECYCLE=1800

# Security
SSL_MODE=prefer
SSL_CERT=/path/to/cert
SSL_KEY=/path/to/key
SSL_ROOT_CERT=/path/to/root_cert
```

3. **Database Setup**
```bash
# Create database
createdb ariesone

# Run migrations
alembic upgrade head
```

## Security Setup

1. **Authentication**
```python
from security.auth import DatabaseAuth

# Create roles and users
auth = DatabaseAuth()
await auth.create_role("app_user", ["SELECT", "INSERT"])
await auth.create_user("user1", "password", ["app_user"])
```

2. **Encryption**
```python
from security.encryption import DatabaseEncryption

# Setup column encryption
encryption = DatabaseEncryption(master_key)
await encryption.setup_column_encryption("users", "ssn")
```

3. **Access Controls**
```python
from security.access import DatabaseAccess

# Enable row-level security
access = DatabaseAccess()
await access.enable_row_level_security(
    "patient_data",
    "org_policy",
    "org_id = current_setting('app.current_org')"
)
```

## Monitoring Setup

1. **Health Checks**
```python
from management.health import check_database_connection

# Check connection health
health = await check_database_connection()
print(f"Database status: {health['status']}")
```

2. **Backup Configuration**
```python
from management.backup import BackupManager

# Setup automated backups
backup = BackupManager(
    backup_dir="/backups",
    retention_days=30,
    encryption_key=key
)
await backup.create_backup()
```

3. **Monitoring Integration**
```python
from management.monitor import DatabaseMonitor

# Collect metrics
monitor = DatabaseMonitor()
metrics = await monitor.collect_all_metrics()
```

## Best Practices

1. **Connection Management**
- Use connection pooling
- Set appropriate pool size
- Configure connection timeouts
- Enable SSL/TLS

2. **Security**
- Use strong passwords
- Enable encryption for sensitive data
- Implement row-level security
- Regular security audits

3. **Performance**
- Monitor query performance
- Use connection pooling
- Regular maintenance
- Index optimization

4. **Backup & Recovery**
- Regular backups
- Test restore procedures
- Monitor backup success
- Encrypt backups

## Troubleshooting

1. **Connection Issues**
- Check network connectivity
- Verify credentials
- Check SSL configuration
- Review connection limits

2. **Performance Problems**
- Check query plans
- Monitor resource usage
- Review connection pool
- Check for locks

3. **Security Concerns**
- Audit user access
- Review encryption
- Check permissions
- Monitor failed logins

## Maintenance

1. **Regular Tasks**
- Backup verification
- Index maintenance
- Security audits
- Performance monitoring

2. **Updates**
- Version upgrades
- Security patches
- Configuration reviews
- Documentation updates

## Support
For additional support:
- Review logs
- Check documentation
- Contact support team
- Submit issue tickets
