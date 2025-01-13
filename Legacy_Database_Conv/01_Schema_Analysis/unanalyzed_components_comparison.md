# Unanalyzed Components Comparison

## Schema Information
- **Schema Name**: DMEWorks
- **Source File**: C:/Projects/AriesOne_SaaS/Analysis_Workspace/Legacy_Database_Source/Schema/DMEWorks_schema.sql
- **Last Modified**: 2025-01-13
- **Character Set**: latin1
- **Collation**: latin1_general_ci

## Unanalyzed Components

### 1. CMN Forms Module
#### Tables
1. tbl_cmnform (Base table)
   - Not implemented
   - Core CMN management
   - Required for medical documentation

2. CMN Form Type Tables
   - tbl_cmnform_0102a through tbl_cmnform_48403
   - 24 specialized form tables
   - No corresponding models
   - Critical for compliance

#### Business Rules
- Form type validation
- Answer validation rules
- Required field logic
- Cross-reference enforcement

### 2. Insurance Processing
#### Tables
1. tbl_ability_eligibility_request
   - Real-time eligibility checking
   - Request/response tracking
   - Not implemented in models

2. tbl_customer_insurance
   - Insurance assignment
   - Coverage periods
   - Missing implementation

#### Views
1. view_eligibility_status
   - Real-time status tracking
   - Not implemented

### 3. System Functions
#### GetAllowableAmount Function
- Complex pricing logic
- Multiple parameters
- Not implemented in services

#### GetQuantityMultiplier Function
- Quantity calculations
- Billing period handling
- Not implemented in services

### 4. Stored Procedures
#### Billing Procedures
1. InvoiceDetails_AddAutoSubmit
   - Auto-submission logic
   - Not implemented

2. InvoiceDetails_AddPayment
   - Payment processing
   - Not implemented

3. InvoiceDetails_InternalAddSubmitted
   - Submission tracking
   - Not implemented

4. InvoiceDetails_RecalculateInternals
   - Balance recalculation
   - Not implemented

### 5. Views
1. view_orderdetails
   - Complex order view
   - Not implemented

2. view_orderdetails_core
   - Core order data
   - Not implemented

3. view_sequence
   - Sequence management
   - Not implemented

### 6. Doctor Management
#### Tables
1. tbl_doctor
   - Basic doctor info
   - Not fully implemented

2. tbl_doctortype
   - Doctor specialties
   - Not implemented

3. tbl_doctor_insurance
   - Insurance relationships
   - Not implemented

## Implementation Impact

### Data Model Changes
1. CMN Forms
   - New models needed
   - Complex relationships
   - Validation rules

2. Insurance Processing
   - Real-time processing
   - Status tracking
   - Response handling

3. Doctor Management
   - Relationship handling
   - Insurance integration
   - Specialty management

### Service Layer Impacts
1. Business Logic Migration
   - Function conversion
   - Procedure migration
   - View implementation

2. API Requirements
   - New endpoints needed
   - Complex queries
   - Real-time processing

### Integration Points
1. External Systems
   - Insurance verification
   - Doctor credentialing
   - CMN processing

2. Internal Systems
   - Billing integration
   - Order processing
   - Patient records
