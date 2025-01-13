# Stored Procedures Modernization Plan

## Overview
Total Components: 78
- Functions: 13
- Procedures: 65

## Functional Categories

### 1. Calculation Functions (13)
- **Amount Calculations**
  - GetAllowableAmount
  - GetAmountMultiplier
  - GetBillableAmount
  - GetInvoiceModifier
  - GetMultiplier
  - GetQuantityMultiplier

- **Date/Period Calculations**
  - GetNewDosTo
  - GetNextDosFrom
  - GetNextDosTo
  - GetPeriodEnd
  - GetPeriodEnd2

- **Order Calculations**
  - OrderedQty2BilledQty
  - OrderedQty2DeliveryQty

### 2. Invoice Management (22)
- **Core Invoice Operations**
  - InvoiceDetails_AddAutoSubmit
  - InvoiceDetails_AddPayment
  - InvoiceDetails_AddSubmitted
  - Invoice_AddAutoSubmit
  - Invoice_AddSubmitted

- **Internal Processing**
  - InvoiceDetails_InternalAddAutoSubmit
  - InvoiceDetails_InternalAddSubmitted
  - InvoiceDetails_InternalReflag
  - InvoiceDetails_InternalWriteoffBalance
  - Invoice_InternalReflag
  - Invoice_InternalUpdateBalance
  - Invoice_InternalUpdatePendingSubmissions

- **Recalculation and Updates**
  - InvoiceDetails_RecalculateInternals
  - InvoiceDetails_RecalculateInternals_Single
  - Invoice_UpdateBalance
  - Invoice_UpdatePendingSubmissions

- **Status Management**
  - InvoiceDetails_Reflag
  - InvoiceDetails_WriteoffBalance
  - Invoice_Reflag
  - InvoiceMustBeSkipped

### 3. Order Processing (8)
- **Core Operations**
  - Order_ConvertDepositsIntoPayments
  - Order_InternalProcess
  - Order_InternalUpdateBalance

- **Status Functions**
  - OrderMustBeClosed
  - OrderMustBeSkipped

### 4. Inventory Management (10)
- **Core Operations**
  - InventoryItem_Clone
  - inventory_adjust_2
  - internal_inventory_transfer

- **Refresh Operations**
  - inventory_refresh
  - inventory_order_refresh
  - inventory_po_refresh

- **Transaction Management**
  - inventory_transaction_add_adjustment
  - fix_serial_transactions

### 5. Insurance and Policy Management (5)
- **Insurance Operations**
  - customer_insurance_fixrank
  - fixInvoicePolicies
  - fixOrderPolicies

### 6. Purchase Orders (2)
- PurchaseOrder_UpdateTotals
- PurchaseOrder_UpdateTransactions

## Implementation Phases

### Phase 1: Core Calculation Layer (Weeks 1-2)
1. All calculation functions (13 components)
2. Unit testing framework
3. Performance benchmarking

### Phase 2: Invoice Management (Weeks 3-5)
1. Core invoice operations
2. Internal processing
3. Recalculation services
4. Status management

### Phase 3: Order Processing (Weeks 6-7)
1. Core order operations
2. Status management
3. Integration with invoicing

### Phase 4: Inventory Management (Weeks 8-9)
1. Core inventory operations
2. Refresh mechanisms
3. Transaction handling

### Phase 5: Supporting Systems (Weeks 10-11)
1. Insurance management
2. Policy handling
3. Purchase order processing

## Modernization Strategy

### For Each Component:
1. Analysis (1 day)
   - Document inputs/outputs
   - Map dependencies
   - Identify business rules

2. Design (1 day)
   - Create service interface
   - Define data contracts
   - Plan error handling

3. Implementation (2-3 days)
   - Write service code
   - Implement error handling
   - Add logging/monitoring

4. Testing (1-2 days)
   - Unit tests
   - Integration tests
   - Performance tests

## Quality Gates

### Each Component Must Pass:
1. Code Coverage > 85%
2. Performance within 10% of legacy
3. All error cases handled
4. Documentation complete
5. Integration tests passing

## Monitoring and Metrics

### Key Metrics:
1. Execution time
2. Error rates
3. Resource usage
4. Transaction volume
5. Concurrent operations

## Risk Management

### High-Risk Areas:
1. Complex calculations
2. Transaction processing
3. Concurrent operations
4. Data consistency

### Mitigation Strategies:
1. Comprehensive testing
2. Staged rollout
3. Monitoring
4. Rollback procedures

## Next Steps

1. Begin Phase 1:
   - Set up development environment
   - Create testing framework
   - Start with GetAllowableAmount function

2. Prepare for Phase 2:
   - Document invoice workflows
   - Map dependencies
   - Create test data
