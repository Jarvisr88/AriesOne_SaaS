# Database Optimization Guidelines

## Query Optimization

### 1. Use SQLAlchemy ORM Efficiently

```python
# Good - Eager loading related data
query = (
    db.query(User)
    .options(joinedload(User.company))
    .filter(User.is_active == True)
)

# Bad - N+1 problem
users = db.query(User).all()
for user in users:
    company = user.company  # Triggers additional query
```

### 2. Optimize SELECT Queries

- Only select needed columns
- Use specific filters early in the query
- Implement pagination
- Use appropriate joins

```python
# Good - Select specific columns
query = db.query(User.id, User.email)

# Good - Early filtering
query = (
    db.query(User)
    .filter(User.company_id == company_id)
    .order_by(User.created_at)
)

# Good - Pagination
query = query.offset(skip).limit(limit)
```

### 3. Use Bulk Operations

```python
# Good - Bulk insert
db.bulk_insert_mappings(User, users_data)

# Good - Bulk update
db.bulk_update_mappings(User, users_updates)
```

### 4. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_preferences(user_id: int) -> Dict:
    return db.query(UserPreferences).filter_by(user_id=user_id).first().to_dict()
```

## Indexing Strategy

### 1. Primary Keys
- Every table must have a primary key
- Use auto-incrementing integers or UUIDs
- Consider using composite keys when necessary

### 2. Foreign Keys
- Always index foreign key columns
- Consider composite indexes for frequently joined columns

### 3. Common Query Patterns
- Index columns used in WHERE clauses
- Index columns used in ORDER BY
- Index columns used in GROUP BY
- Consider covering indexes for frequently used queries

### 4. Index Types

#### B-tree Indexes (Default)
- Best for equality and range queries
- Good for sorting and uniqueness constraints

```sql
CREATE INDEX idx_user_email ON users (email);
CREATE INDEX idx_user_company ON users (company_id, created_at);
```

#### Partial Indexes
- Index subset of rows meeting a condition
- Reduces index size and maintenance overhead

```sql
CREATE INDEX idx_active_users ON users (id) WHERE is_active = true;
```

#### Expression Indexes
- Index result of an expression
- Optimize queries using functions

```sql
CREATE INDEX idx_email_lower ON users (lower(email));
```

## Performance Monitoring

### 1. Query Performance
- Monitor slow queries (> 100ms)
- Analyze query plans
- Track query patterns

### 2. Connection Pool
- Monitor pool utilization
- Track connection lifecycle
- Implement connection timeouts

### 3. Database Statistics
- Track table and index sizes
- Monitor cache hit ratios
- Analyze buffer pool usage

## Best Practices

### 1. Schema Design
- Use appropriate data types
- Implement proper constraints
- Normalize data appropriately
- Consider denormalization for performance

### 2. Query Patterns
- Use prepared statements
- Implement retry logic for transient failures
- Handle deadlocks gracefully
- Use appropriate transaction isolation levels

### 3. Maintenance
- Regular VACUUM and ANALYZE
- Monitor and update statistics
- Archive old data
- Implement partitioning for large tables

## Example Migrations

```python
"""create_users_table

Revision ID: 1234567890ab
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_user_email', 'users', ['email'], unique=True)
    op.create_index('idx_user_company', 'users', ['company_id', 'created_at'])
    op.create_index(
        'idx_active_users',
        'users',
        ['id'],
        postgresql_where=sa.text('is_active = true')
    )

def downgrade():
    op.drop_index('idx_active_users')
    op.drop_index('idx_user_company')
    op.drop_index('idx_user_email')
    op.drop_table('users')
```

## Query Examples

### 1. Complex Joins
```python
query = (
    db.query(User, Company.name)
    .join(Company)
    .options(contains_eager(User.company))
    .filter(User.is_active == True)
    .order_by(User.created_at.desc())
)
```

### 2. Aggregations
```python
query = (
    db.query(
        Company.id,
        Company.name,
        func.count(User.id).label('user_count'),
        func.max(User.created_at).label('latest_user')
    )
    .join(User)
    .group_by(Company.id)
    .having(func.count(User.id) > 0)
)
```

### 3. Window Functions
```python
from sqlalchemy.sql import over

query = (
    db.query(
        User,
        func.row_number()
        .over(
            partition_by=User.company_id,
            order_by=User.created_at.desc()
        ).label('rank')
    )
)
```

## Monitoring Queries

```python
# Track slow queries
@event.listens_for(engine, 'after_cursor_execute')
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop()
    if total_time > settings.SLOW_QUERY_THRESHOLD:
        logger.warning(f"Slow query detected: {statement}")
        logger.warning(f"Parameters: {parameters}")
        logger.warning(f"Execution time: {total_time}s")
```
