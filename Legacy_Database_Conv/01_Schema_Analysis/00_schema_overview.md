# Legacy Schema Overview

## Database Structure
The legacy system consists of three main databases:

1. `c01` (Main Application Database)
   - Primary business logic and data storage
   - Customer management
   - Order processing
   - Billing and insurance
   - CMN form management
   - Inventory tracking

2. `repository` (Batch Processing Database)
   - Batch operation management
   - Workflow tracking
   - Regional processing

3. `dmeworks` (Core DME Database)
   - Doctor management
   - Insurance company management
   - Core DME business rules

## Schema Characteristics
- Character Set: latin1
- Collation: latin1_general_ci
- Engine: InnoDB
- Timestamp handling: Uses CURRENT_TIMESTAMP for last update tracking
- Audit fields: LastUpdateUserID and LastUpdateDatetime common across tables

## Core Business Areas

### 1. Customer Management
- Customer demographics
- Insurance information
- Billing preferences
- Medical records (ICD9/ICD10)

### 2. Order Processing
- Order creation and tracking
- Order details management
- Serial number tracking
- Authorization handling
- Billing code management

### 3. Billing and Insurance
- Insurance company management
- Payment processing
- Claim submission
- Authorization tracking
- Batch payment handling

### 4. Inventory Management
- Item tracking
- Serial number management
- Warehouse management
- Price code handling

### 5. Medical Documentation
- CMN form management
- Multiple CMN types
- Doctor orders
- Medical necessity tracking

### 6. Provider Management
- Doctor information
- Facility management
- Location tracking
- Referral management

## Technical Characteristics

### Data Types
- Extensive use of:
  - INT(11) for IDs
  - VARCHAR(50) for names/codes
  - DECIMAL(18,2) for monetary values
  - DATETIME/TIMESTAMP for temporal data
  - ENUM for constrained choices
  - MEDIUMTEXT for large text fields

### Relationships
- Heavy use of foreign keys
- Complex many-to-many relationships
- Hierarchical data structures

### Business Logic
- Stored procedures for complex operations
- Triggers for data integrity
- Views for simplified data access
- Functions for calculations

## Migration Considerations

### Data Integrity
- Foreign key relationships
- Default values
- NOT NULL constraints
- Unique constraints

### Business Rules
- Complex payment processing
- Insurance claim handling
- Authorization management
- Billing cycles

### Performance Aspects
- Index usage
- Table partitioning
- Query optimization
- Transaction management

## Next Steps
1. Detailed table analysis
2. Business rule documentation
3. Data flow mapping
4. Migration strategy development
