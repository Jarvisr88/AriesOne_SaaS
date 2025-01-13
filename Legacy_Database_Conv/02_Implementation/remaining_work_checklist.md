# Schema Modernization Remaining Work Checklist

## Project Information
- **Start Date**: 2025-01-13
- **Priority**: High
- **Risk Level**: Medium

## Pre-Implementation Analysis

### Dependencies Assessment
- [x] CMN Forms module dependencies mapped
- [x] Insurance processing integration points identified
- [ ] Doctor management relationships documented
- [ ] System function dependencies analyzed

## Implementation Checklist

### 1. CMN Forms Module
#### Base Implementation
- [x] Create CMNForm base model
- [x] Implement form type validation
- [x] Add form state management
- [x] Create form routing system

#### Form Type Implementation
- [x] Create models for all form types (24)
- [x] Implement validation rules
- [x] Add cross-reference checks
- [x] Create form-specific services

#### Testing
- [x] Unit tests for models
- [x] Validation rule tests
- [x] Integration tests
- [x] Form submission tests

### 2. Insurance Processing
#### Eligibility System
- [x] Create eligibility request model
- [x] Implement real-time processing
- [x] Add response handling
- [x] Create status tracking

#### Insurance Management
- [x] Implement customer insurance model
- [x] Add coverage period handling
- [x] Create insurance assignment system
- [x] Implement verification system

#### Testing
- [x] Eligibility request tests
- [x] Insurance policy tests
- [x] Integration tests
- [x] Verification workflow tests

### 3. System Functions
#### GetAllowableAmount
- [x] Analyze current implementation
- [x] Create service method
- [x] Implement pricing logic
- [x] Add parameter handling

#### GetQuantityMultiplier
- [x] Analyze current implementation
- [x] Create service method
- [x] Add calculation logic
- [x] Implement period handling

#### GetAllowableAmount
- [x] Implement base function
- [x] Add sale/rent type handling
- [x] Include flat rate support
- [x] Create unit tests

#### GetBillingAmount
- [x] Implement calculation logic
- [x] Add tax handling
- [x] Include adjustments
- [x] Create unit tests

#### CalculateRental
- [x] Implement period calculation
- [x] Add rate adjustments
- [x] Include purchase options
- [x] Create unit tests

#### GetInventoryValue
- [x] Implement valuation methods
- [x] Add cost calculations
- [x] Include reorder points
- [x] Create unit tests

#### Testing
- [x] Unit tests for calculations
- [x] Edge case testing
- [x] Integration tests
- [x] Performance tests

### 4. Doctor Management
#### Base Implementation
- [x] Create doctor models
- [x] Implement provider types
- [x] Add credential tracking
- [x] Create service layer

#### Provider Numbers
- [x] Implement number types
- [x] Add expiration tracking
- [x] Create verification system
- [x] Add status management

#### Integration
- [x] Link with CMN forms
- [x] Connect to orders
- [x] Add API endpoints
- [x] Implement security

#### Testing
- [x] Unit tests for models
- [x] Credential verification tests
- [x] Integration tests
- [x] API endpoint tests

### 5. Stored Procedures
#### Billing Procedures
- [ ] Implement AddAutoSubmit
- [ ] Create AddPayment service
- [ ] Add submission tracking
- [ ] Implement recalculation logic

#### Testing
- [ ] Unit tests for each procedure
- [ ] Transaction tests
- [ ] Integration tests
- [ ] Performance tests

### 6. Views
#### Order Views
- [ ] Implement view_orderdetails
- [ ] Create view_orderdetails_core
- [ ] Add view_sequence
- [ ] Create indexes

#### Testing
- [ ] Query performance tests
- [ ] Data accuracy tests
- [ ] Integration tests
- [ ] Load tests

## Quality Gates

### Documentation
- [ ] API documentation
- [ ] Integration guides
- [ ] Testing documentation
- [ ] Deployment guides

### Performance
- [ ] Query optimization
- [ ] Index strategy
- [ ] Caching implementation
- [ ] Load testing

### Security
- [ ] Access control
- [ ] Data encryption
- [ ] Audit logging
- [ ] Compliance checks

## Migration Strategy

### Data Migration
- [ ] CMN forms data
- [ ] Insurance records
- [ ] Doctor records
- [ ] Historical data

### Validation
- [ ] Data integrity checks
- [ ] Business rule validation
- [ ] Integration testing
- [ ] User acceptance testing

## Timeline Estimates
- CMN Forms: 3 weeks
- Insurance Processing: 2 weeks
- System Functions: 1 week
- Doctor Management: 2 weeks
- Stored Procedures: 2 weeks
- Views: 1 week

Total Estimated Time: 11 weeks
