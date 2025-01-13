# CMN Forms Analysis

## Schema Information
- **Schema Name**: c01
- **Source File**: DMEWorks_schema.sql
- **Last Modified**: 2025-01-13
- **Character Set**: latin1
- **Collation**: latin1_general_ci

## Core Components

### 1. Base CMN Form Table (tbl_cmnform)
#### Structure
- Primary Key: ID (INT, auto-increment)
- Form Type: CMNType (ENUM)
  - 24 different form types
  - Examples: DMERC 01.02A, DME 484.03
- Dates:
  - InitialDate (DATE)
  - RevisedDate (DATE)
- Status tracking
- Audit fields

### 2. Form Type Tables
All form tables follow pattern: tbl_cmnform_[type]
Each has unique answer fields based on form type.

#### Common Patterns
1. Answer Field Types:
   - ENUM('Y', 'N', 'D') for Yes/No/Default
   - DATE for date fields
   - VARCHAR for text responses
   - INT for numeric responses

2. Relationships:
   - Each form links to base table via CMNFormID
   - Forms link to Orders
   - Forms link to Customers

### 3. Business Rules
1. Form Validation:
   - Required fields vary by form type
   - Answer validation specific to field type
   - Date validations for Initial/Revised dates

2. Form State Management:
   - Status tracking
   - Revision handling
   - Expiration rules

3. Integration Points:
   - Order system integration
   - Billing system integration
   - Insurance processing integration

## Implementation Requirements

### 1. Models Layer
#### Base CMN Model
```python
class CMNForm(Base):
    __tablename__ = 'tbl_cmnform'
    id = Column(Integer, primary_key=True)
    cmn_type = Column(Enum(CMNFormType))
    initial_date = Column(Date)
    revised_date = Column(Date)
    # Additional fields
```

#### Form Type Models
- One model per form type
- Inherit from base CMN model
- Type-specific validation rules

### 2. Service Layer
#### Core Services
1. Form Management:
   - Creation
   - Updates
   - State management
   - Validation

2. Integration Services:
   - Order integration
   - Billing integration
   - Insurance processing

### 3. API Layer
#### Endpoints Required
1. Form Management:
   - GET /api/v1/cmn-forms
   - POST /api/v1/cmn-forms
   - GET /api/v1/cmn-forms/{id}
   - PUT /api/v1/cmn-forms/{id}
   - DELETE /api/v1/cmn-forms/{id}

2. Form Type Specific:
   - GET /api/v1/cmn-forms/types
   - GET /api/v1/cmn-forms/type/{type}

## Implementation Strategy

### Phase 1: Core Infrastructure
1. Base Models:
   - CMNForm base class
   - Enum definitions
   - Common validators

2. Database Migrations:
   - Character set handling
   - Index creation
   - Constraint implementation

### Phase 2: Form Type Implementation
1. Individual Form Models:
   - Type-specific fields
   - Validation rules
   - Business logic

2. Services:
   - CRUD operations
   - Validation services
   - Integration handlers

### Phase 3: API Development
1. REST Endpoints:
   - Form management
   - Type-specific endpoints
   - Validation endpoints

2. Documentation:
   - API documentation
   - Integration guides
   - Testing documentation

## Testing Strategy

### 1. Unit Tests
- Model validation
- Business rule enforcement
- Form type specific logic

### 2. Integration Tests
- Database operations
- API endpoints
- Service integration

### 3. Validation Tests
- Form type validation
- Data integrity
- Business rule compliance

## Migration Considerations

### 1. Data Migration
- Character set conversion
- Date format standardization
- Enum value mapping

### 2. Integration Migration
- Order system updates
- Billing system updates
- Insurance processing updates

## Timeline Estimate
- Phase 1: 1 week
- Phase 2: 1.5 weeks
- Phase 3: 0.5 weeks
Total: 3 weeks
