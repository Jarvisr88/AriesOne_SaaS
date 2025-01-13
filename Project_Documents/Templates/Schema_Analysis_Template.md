# Schema Analysis Template

## Schema Information
- **Schema Name**: [Name of the schema]
- **Source File**: [Full path to schema file]
- **Last Modified**: [Last modification date]
- **Character Set**: [Schema character set]
- **Collation**: [Schema collation]

## Schema Overview
### Database Structure
- List of databases
- Purpose of each database
- Cross-database relationships

### Object Types Analysis
#### Tables
For each table:
- Table name
- Primary purpose
- Column definitions
- Primary keys
- Foreign keys
- Indexes
- Constraints
- Implementation status
- Cross-reference to implementation files

#### Views
For each view:
- View name
- Purpose
- Base tables
- Implementation status
- Cross-reference to implementation files

#### Stored Procedures
For each procedure:
- Procedure name
- Purpose
- Parameters
- Business logic
- Implementation status
- Cross-reference to implementation files

#### Functions
For each function:
- Function name
- Purpose
- Parameters
- Return type
- Business logic
- Implementation status
- Cross-reference to implementation files

### Data Types and Patterns
- Common data types used
- Enum definitions
- Custom types
- Default values
- Null handling

### Business Rules
- Constraints
- Triggers
- Computed columns
- Complex relationships
- Implementation status
- Cross-reference to implementation files

## Implementation Analysis
### Models
- List of implemented models
- Missing models
- Mapping accuracy
- Data type conversions

### Database Access
- ORM implementation
- Query patterns
- Transaction handling
- Connection management

### Migration Considerations
- Character set conversion
- Collation changes
- Default value handling
- Constraint implementation
- Index strategy

## Dependencies
### Internal Dependencies
- Cross-table relationships
- View dependencies
- Procedure dependencies
- Function dependencies

### External Dependencies
- External systems
- API integrations
- File system dependencies
- Third-party services

## Security Considerations
- Access control
- Data encryption
- Audit logging
- Sensitive data handling

## Performance Considerations
- Index coverage
- Query optimization
- Data volume handling
- Caching strategy

## Documentation Status
- Schema documentation
- API documentation
- Business rule documentation
- Integration documentation
