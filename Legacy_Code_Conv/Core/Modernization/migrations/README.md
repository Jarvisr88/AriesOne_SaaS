# Database Migrations

Version: 1.0.0
Last Updated: 2025-01-10

This directory contains database migration scripts for the AriesOne SaaS application using Alembic.

## Migration Scripts

### 1. Initial Schema (001_initial_schema.py)
- Base tables: users, tenants, inventory_items, orders, order_items, audit_logs
- Indexes for performance optimization
- UUID support with uuid-ossp extension

### 2. Tenant Features (002_add_tenant_features.py)
- Added tenant features and settings
- API key management
- Billing cycle tracking
- Tenant-specific settings storage

### 3. Inventory Tracking (003_add_inventory_tracking.py)
- Inventory transaction history
- Location management
- SKU and barcode tracking
- Reorder point management

## Running Migrations

### Prerequisites
1. Install dependencies:
```bash
pip install alembic psycopg2-binary
```

2. Configure database connection:
```bash
# Edit alembic.ini with your database URL
sqlalchemy.url = postgresql://user:pass@localhost/db_name
```

### Commands

#### Upgrade Database
```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade 002_add_tenant_features
```

#### Downgrade Database
```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade 001_initial_schema
```

#### View Migration History
```bash
# Show current version
alembic current

# Show history
alembic history --verbose
```

#### Create New Migration
```bash
alembic revision -m "description"
```

## Rollback Procedures

### Before Migration
1. Create database backup:
```bash
pg_dump -Fc db_name > backup.dump
```

2. Test migration in staging:
```bash
psql -d staging_db -f migration.sql
```

### Rollback Steps
1. Revert migration:
```bash
alembic downgrade -1
```

2. Restore from backup if needed:
```bash
pg_restore -d db_name backup.dump
```

## Best Practices

### Migration Design
1. Make migrations reversible
2. Test both upgrade and downgrade
3. Keep migrations atomic
4. Include data migrations
5. Add appropriate indexes

### Data Safety
1. Backup before migration
2. Test in staging first
3. Schedule during low traffic
4. Monitor system during migration
5. Have rollback plan ready

### Performance
1. Use batching for large datasets
2. Add indexes before data migration
3. Remove indexes after data migration
4. Monitor transaction logs
5. Consider table partitioning

## Troubleshooting

### Common Issues
1. Lock timeout
   - Increase statement timeout
   - Use batching
   - Schedule during off-peak

2. Space issues
   - Monitor disk space
   - Clean old data
   - Use table partitioning

3. Connection issues
   - Check connection limits
   - Monitor connection pool
   - Adjust timeout settings

### Recovery Steps
1. Check migration logs
2. Identify failure point
3. Fix root cause
4. Restore if needed
5. Retry migration

## Monitoring

### During Migration
1. Database connections
2. Lock queues
3. Transaction logs
4. System resources
5. Application errors

### After Migration
1. Data consistency
2. Application functionality
3. Performance metrics
4. Error rates
5. Business operations

## Maintenance

Regular tasks:
1. Clean old migrations
2. Update dependencies
3. Test recovery procedures
4. Review performance
5. Update documentation
