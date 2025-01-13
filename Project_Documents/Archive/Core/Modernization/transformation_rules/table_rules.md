# Table System Transformation Rules

## Table Definition Transformation

### Legacy to Modern Mapping
1. Table Structure:
   ```
   Legacy (TableDefinition)           Modern (TableDefinition)
   ------------------------           ----------------------
   TableID -> id
   TableName -> name
   Description -> description
   Columns -> schema
   PrimaryKey -> primary_key
   ForeignKeys -> foreign_keys
   Indexes -> indexes
   ```

2. Column Definition:
   ```
   Legacy (ColumnDefinition)          Modern (ColumnDefinition)
   ------------------------           ----------------------
   ColumnID -> name
   DataType -> data_type
   Length -> length
   Precision -> precision
   Scale -> scale
   IsNullable -> is_nullable
   DefaultValue -> default_value
   ```

### Data Type Mapping
1. SQL Server to PostgreSQL:
   ```
   Legacy                            Modern
   ------------------------           ----------------------
   varchar -> VARCHAR
   nvarchar -> VARCHAR
   char -> CHAR
   nchar -> CHAR
   int -> INTEGER
   bigint -> BIGINT
   decimal -> DECIMAL
   float -> FLOAT
   datetime -> TIMESTAMP
   date -> DATE
   bit -> BOOLEAN
   varbinary -> BYTEA
   ```

2. Type Parameters:
   ```json
   {
     "VARCHAR": { "max_length": 255 },
     "CHAR": { "length": 1 },
     "DECIMAL": { "precision": 18, "scale": 2 },
     "TIMESTAMP": { "timezone": true }
   }
   ```

## Schema Management

### Constraint Transformation
1. Primary Keys:
   ```
   Legacy                            Modern
   ------------------------           ----------------------
   CONSTRAINT PK_Name               PRIMARY KEY
   CLUSTERED                        (not applicable)
   NONCLUSTERED                     (not applicable)
   ```

2. Foreign Keys:
   ```sql
   -- Legacy
   CONSTRAINT FK_Name FOREIGN KEY (Column)
   REFERENCES Table (Column)
   ON DELETE CASCADE
   ON UPDATE CASCADE

   -- Modern
   FOREIGN KEY (Column)
   REFERENCES Table (Column)
   ON DELETE CASCADE
   ON UPDATE CASCADE
   ```

3. Indexes:
   ```sql
   -- Legacy
   CREATE [UNIQUE] [CLUSTERED/NONCLUSTERED] INDEX IX_Name
   ON Table (Column) [INCLUDE (Columns)]

   -- Modern
   CREATE [UNIQUE] INDEX ix_name
   ON table (column)
   ```

### Migration Rules
1. Version Control:
   ```
   1. Sequential version numbers
   2. Descriptive migration names
   3. Up and down migrations
   4. Dependencies tracking
   ```

2. Data Migration:
   ```
   1. Preserve data during type changes
   2. Handle default values
   3. Transform data if needed
   4. Validate after migration
   ```

## Schema Validation Rules

### Naming Conventions
1. Identifiers:
   ```
   Tables: lowercase, underscore_separated
   Columns: lowercase, underscore_separated
   Indexes: ix_table_column
   Foreign Keys: fk_table_column
   ```

2. Length Limits:
   ```
   Table names: 63 characters
   Column names: 63 characters
   Index names: 63 characters
   Constraint names: 63 characters
   ```

### Constraint Rules
1. Primary Keys:
   - Required for all tables
   - Prefer integer or UUID
   - Auto-incrementing when possible

2. Foreign Keys:
   - Match referenced column type
   - Index foreign key columns
   - Define ON DELETE/UPDATE actions

3. Indexes:
   - Index foreign keys
   - Index frequently queried columns
   - Consider covering indexes
   - Monitor index usage

## Performance Rules

### Query Optimization
1. Index Guidelines:
   ```
   1. Index foreign keys
   2. Index search columns
   3. Index sort columns
   4. Consider composite indexes
   5. Monitor index usage
   ```

2. Data Types:
   ```
   1. Use smallest sufficient type
   2. Fixed-length for known sizes
   3. Consider storage implications
   4. Use appropriate precision
   ```

### Storage Optimization
1. Column Rules:
   ```
   1. Appropriate data types
   2. Normalize when beneficial
   3. Consider compression
   4. Use constraints
   ```

2. Table Rules:
   ```
   1. Appropriate partitioning
   2. Regular maintenance
   3. Monitor growth
   4. Archive strategy
   ```
