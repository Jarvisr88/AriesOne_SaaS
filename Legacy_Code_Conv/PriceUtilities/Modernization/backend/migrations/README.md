# Database Migrations

This directory contains database migrations for the Price Utilities SaaS application.

## Structure

- `versions/`: Contains numbered migration scripts
- `env.py`: Alembic environment configuration
- `alembic.ini`: Alembic configuration file

## Migration Files

1. `001_initial_schema.py`: Creates initial database schema
   - Price list table
   - ICD codes table
   - Parameters table
   - Audit log table
   - Users table
   - Indexes and constraints

2. `002_data_migration.py`: Migrates data from legacy system
   - Creates admin user
   - Migrates price list data
   - Migrates ICD codes
   - Migrates parameters
   - Creates audit log entries

## Running Migrations

1. Set up environment:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/price_utilities"
   ```

2. Run migrations:
   ```bash
   # Apply all migrations
   alembic upgrade head

   # Rollback last migration
   alembic downgrade -1

   # Rollback to specific version
   alembic downgrade <version_id>
   ```

3. Create new migration:
   ```bash
   alembic revision -m "description"
   ```

## Data Migration

The data migration script expects legacy data files in CSV format:
- `legacy_data/price_list.csv`
- `legacy_data/icd_codes.csv`
- `legacy_data/parameters.csv`

### CSV File Formats

#### price_list.csv
```csv
item_id,description,base_price,currency,quantity_breaks
```

#### icd_codes.csv
```csv
code,description,price_modifier
```

#### parameters.csv
```csv
name,value,parameter_type,description
```

## Troubleshooting

1. Migration fails:
   ```bash
   # Check current state
   alembic current

   # View migration history
   alembic history

   # Show SQL for next migration
   alembic upgrade head --sql
   ```

2. Data migration issues:
   - Verify CSV file formats
   - Check data types
   - Review error logs
