# Database Schema Transformations

## Address Schema

### Legacy to Modern Mapping
```sql
-- Legacy Table
CREATE TABLE Addresses (
    ID INT PRIMARY KEY,
    Address1 VARCHAR(100),
    Address2 VARCHAR(100),
    City VARCHAR(50),
    State CHAR(2),
    ZipCode VARCHAR(10)
);

-- Modern Schema
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    address_line1 VARCHAR(100) NOT NULL,
    address_line2 VARCHAR(100),
    city VARCHAR(50) NOT NULL,
    state CHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_state CHECK (state ~ '^[A-Z]{2}$'),
    CONSTRAINT valid_zip CHECK (zip_code ~ '^\d{5}(-\d{4})?$')
);
```

### Schema Evolution Rules
1. Column Naming
   - Convert PascalCase to snake_case
   - Use descriptive names
   - Follow PostgreSQL conventions

2. Constraints
   - Add NOT NULL where appropriate
   - Add CHECK constraints for validation
   - Use appropriate data types

3. Auditing
   - Add created_at timestamp
   - Add updated_at timestamp
   - Add user tracking if needed

## Name Schema

### Legacy to Modern Mapping
```sql
-- Legacy Table
CREATE TABLE Names (
    ID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    MiddleName VARCHAR(50),
    LastName VARCHAR(50),
    Suffix VARCHAR(10),
    CourtesyTitle VARCHAR(10)
);

-- Modern Schema
CREATE TABLE names (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    middle_initial CHAR(1),
    last_name VARCHAR(50) NOT NULL,
    suffix VARCHAR(4),
    courtesy_title VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_suffix CHECK (suffix IN ('Jr.', 'Sr.', 'II', 'III', 'IV')),
    CONSTRAINT valid_courtesy CHECK (courtesy_title IN ('Mr.', 'Mrs.', 'Miss', 'Dr.', 'Rev.'))
);
```

### Schema Evolution Rules
1. Column Modifications
   - Convert MiddleName to middle_initial
   - Add validation constraints
   - Optimize data types

2. Data Migration
   - Extract first letter of middle name
   - Standardize suffixes
   - Validate courtesy titles

3. Indexing Strategy
   - Add index on last_name
   - Add index on (last_name, first_name)
   - Consider partial indexes

## Map Provider Schema

### Modern Schema
```sql
CREATE TABLE map_providers (
    id SERIAL PRIMARY KEY,
    provider_name VARCHAR(50) NOT NULL,
    api_key VARCHAR(255),
    base_url VARCHAR(255) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_provider CHECK (provider_name IN ('google', 'bing', 'openstreetmap'))
);

CREATE TABLE map_requests (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES map_providers(id),
    request_type VARCHAR(20) NOT NULL,
    query TEXT NOT NULL,
    response_status INTEGER,
    response_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_request_type CHECK (request_type IN ('geocode', 'search', 'reverse'))
);
```

### Schema Evolution Rules
1. Provider Management
   - Track API usage
   - Monitor provider status
   - Manage provider priorities

2. Request Logging
   - Track all map requests
   - Store response data
   - Enable request analysis

3. Performance Optimization
   - Use appropriate indexes
   - Implement data archival
   - Optimize JSONB storage
