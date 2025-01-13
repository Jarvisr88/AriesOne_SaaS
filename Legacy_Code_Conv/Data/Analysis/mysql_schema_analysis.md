# MySQL Schema Analysis
Version: 1.0.0
Date: 2025-01-13
Status: In Progress

## Overview
Analysis of the existing MySQL database schema used in the AriesOne legacy system.

## Schema Structure

### Authentication & Authorization
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    company_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100) NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100) NOT NULL
);

CREATE TABLE user_roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);
```

### Company & Location Management
```sql
CREATE TABLE companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100) NOT NULL
);

CREATE TABLE locations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    address_line1 VARCHAR(100) NOT NULL,
    address_line2 VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100) NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

### Price Management
```sql
CREATE TABLE price_lists (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATETIME NOT NULL,
    expiration_date DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100) NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE price_list_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    price_list_id INT NOT NULL,
    item_code VARCHAR(20) NOT NULL,
    description VARCHAR(255) NOT NULL,
    unit_price INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL,
    updated_by VARCHAR(100) NOT NULL,
    FOREIGN KEY (price_list_id) REFERENCES price_lists(id)
);
```

## Data Types Used
1. Integer Types
   - INT: Primary keys, foreign keys, counts
   - TINYINT/BOOLEAN: Flags and boolean values

2. String Types
   - VARCHAR(50): Usernames, codes
   - VARCHAR(100): Names, emails
   - VARCHAR(255): Longer text, hashes
   - TEXT: Descriptions, large text

3. Date/Time Types
   - DATETIME: Timestamps, effective dates
   - Default CURRENT_TIMESTAMP
   - ON UPDATE CURRENT_TIMESTAMP

## Relationships
1. Company-centric Design
   - Companies -> Users (One-to-Many)
   - Companies -> Locations (One-to-Many)
   - Companies -> Price Lists (One-to-Many)

2. User Management
   - Users -> Roles (Many-to-Many via user_roles)
   - Users -> Companies (Many-to-One)

3. Price Management
   - Price Lists -> Items (One-to-Many)
   - Price Lists -> Companies (Many-to-One)

## Constraints
1. Primary Keys
   - All tables use auto-incrementing INT

2. Foreign Keys
   - Proper referential integrity
   - No CASCADE operations defined

3. Unique Constraints
   - username, email in users
   - name in roles
   - code in companies
   - code in price_lists

4. Not Null Constraints
   - Most fields are NOT NULL
   - Audit fields required
   - Only optional fields:
     - address_line2 in locations
     - expiration_date in price_lists

## Audit Trail
All tables include:
- created_at: Creation timestamp
- updated_at: Last update timestamp
- created_by: User who created
- updated_by: User who last updated

## Migration Considerations
1. Data Type Mapping
   - INT -> Integer in PostgreSQL
   - VARCHAR -> VARCHAR in PostgreSQL
   - DATETIME -> TIMESTAMP in PostgreSQL
   - TEXT -> TEXT in PostgreSQL

2. Index Requirements
   - Primary key indexes
   - Foreign key indexes
   - Unique constraint indexes
   - Custom indexes needed:
     - (company_id, is_active) on locations
     - (price_list_id, item_code) on price_list_items
     - (effective_date, expiration_date) on price_lists

3. Constraint Changes
   - Add ON DELETE/UPDATE actions
   - Add CHECK constraints
   - Add EXCLUSION constraints

4. Performance Optimization
   - Partitioning for price_list_items
   - Materialized views for reporting
   - Connection pooling setup

## Security Requirements
1. Row-Level Security
   - Company-based isolation
   - User-based access control

2. Column-Level Security
   - Encryption for sensitive data
   - Masking for certain users

3. Audit Requirements
   - Maintain existing audit trail
   - Add transaction logging
   - Add change tracking

## Testing Strategy
1. Schema Validation
   - Table structure tests
   - Constraint tests
   - Index tests

2. Data Migration
   - Completeness tests
   - Integrity tests
   - Performance tests

3. Integration
   - Application compatibility
   - Query performance
   - Connection management
