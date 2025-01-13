# Stored Procedures and Functions Modernization Tracker

## Status Key
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Completed
- ⚠️ Blocked
- 🔵 In Review

## Progress Summary
- Total Components: 80
- Not Started: 53
- In Progress: 5
- Completed: 22
- Blocked: 0
- In Review: 0

## 1. Calculation Functions

### Amount Calculations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CF001 | GetAllowableAmount | Function | 🟢 | None | High | P1 | 2025-01-13 | 2025-01-13 | Modernized to Python class with full test coverage |
| CF002 | GetAmountMultiplier | Function | 🟢 | None | Medium | P1 | 2025-01-13 | 2025-01-13 | Modernized with frequency enums and full test coverage |
| CF003 | GetBillableAmount | Function | 🟢 | None | High | P1 | 2025-01-13 | 2025-01-13 | Modernized with tax/discount support and full test coverage |
| CF004 | GetInvoiceModifier | Function | 🟢 | None | Medium | P1 | 2025-01-13 | 2025-01-13 | Modernized with business rules engine and full test coverage |
| CF005 | GetMultiplier | Function | 🟢 | None | Medium | P2 | 2025-01-13 | 2025-01-13 | Modernized with proration and rounding options |
| CF006 | GetQuantityMultiplier | Function | 🟢 | None | Medium | P2 | 2025-01-13 | 2025-01-13 | Modernized with quantity rules and flat rate support |
| CF007 | CalculateNextBillingDate | Function | 🟢 | Date tables | Low | P1 | 2025-01-13 | 2025-01-13 | Date calc |
| CF008 | CalculateDeliveryDate | Function | 🟢 | Date tables | Low | P1 | 2025-01-13 | 2025-01-13 | Delivery calc |
| CF009 | CalculateShipDate | Function | 🟢 | Date tables | Low | P1 | 2025-01-13 | 2025-01-13 | Ship calc |
| CF010 | GetBusinessDays | Function | 🟢 | Date tables | Low | P1 | 2025-01-13 | 2025-01-13 | Business days |
| CF011 | IsHoliday | Function | 🟢 | Date tables | Low | P1 | 2025-01-13 | 2025-01-13 | Holiday check |
| CF012 | IsBusinessDay | Function | 🟢 | Date tables | Low | P1 | 2025-01-13 | 2025-01-13 | Business check |

### Date/Period Calculations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CF013 | GetNewDosTo | Function | 🟢 | None | Low | P2 | 2025-01-13 | 2025-01-13 | Modernized with frequency support and end date handling |
| CF014 | GetNextDosFrom | Function | 🟢 | None | Low | P2 | 2025-01-13 | 2025-01-13 | Modernized with frequency-aware date calculations |
| CF015 | GetNextDosTo | Function | 🟢 | None | Low | P2 | 2025-01-13 | 2025-01-13 | Modernized with period length maintenance |
| CF016 | GetPeriodEnd | Function | 🟢 | None | Low | P2 | 2025-01-13 | 2025-01-13 | Modernized with calendar alignment support |
| CF017 | GetPeriodEnd2 | Function | 🟢 | None | Medium | P2 | 2025-01-13 | 2025-01-13 | Modernized with min days and partial period support |

### Order Calculations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CF018 | OrderedQty2BilledQty | Function | 🟢 | None | Medium | P2 | 2025-01-13 | 2025-01-13 | Modernized with constraints and rounding support |
| CF019 | GetOrderedQty | Function | 🟢 | None | Medium | P2 | 2025-01-13 | 2025-01-13 | Modernized with multiple billing types |
| CF020 | OrderedQty2DeliveryQty | Function | 🟢 | None | Medium | P2 | 2025-01-13 | 2025-01-13 | Modernized with delivery schedules |

## 2. Invoice Management

### Core Invoice Operations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IM001 | InvoiceDetails_AddAutoSplit | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Split quantities |
| IM002 | InvoiceDetails_AddPayment | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Payment processing |
| IM003 | InvoiceDetails_AddSubmitted | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Submission handling |
| IM004 | Invoice_AddAutoSubmit | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Invoice auto submission |
| IM005 | Invoice_AddSubmitted | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Invoice submission |

### Internal Processing
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IM006 | InvoiceDetails_InternalAddAutoSubmit | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Internal auto submission |
| IM007 | InvoiceDetails_InternalAddSubmitted | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Internal submission |
| IM008 | InvoiceDetails_InternalReflag | Procedure | 🟢 | Invoice tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Status update |
| IM009 | InvoiceDetails_InternalWriteoffBalance | Procedure | 🟢 | Invoice tables | High | P2 | 2025-01-13 | 2025-01-13 | Balance writeoff |
| IM010 | Invoice_InternalReflag | Procedure | 🟢 | Invoice tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Invoice status update |
| IM011 | Invoice_InternalUpdateBalance | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Balance update |
| IM012 | Invoice_InternalUpdatePendingSubmissions | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Submission update |

### Recalculation and Updates
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IM013 | InvoiceDetails_RecalculateInternals | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Recalculation logic |
| IM014 | InvoiceDetails_RecalculateInternals_Single | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Single record recalc |
| IM015 | Invoice_UpdateBalance | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Balance update |
| IM016 | Invoice_UpdatePendingSubmissions | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Submission update |

### Status Management
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IM017 | Invoice_UpdateStatus | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Status updates |
| IM018 | Invoice_ValidateStatus | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Status validation |
| IM019 | Invoice_CancelInvoice | Procedure | 🟢 | Invoice tables | High | P1 | 2025-01-13 | 2025-01-13 | Cancellation |
| IM020 | InvoiceMustBeSkipped | Function | 🟢 | Invoice tables | Low | P3 | 2025-01-13 | 2025-01-13 | Skip logic |
| IM021 | InvoiceIsProcessable | Function | 🟢 | Invoice tables | Low | P3 | 2025-01-13 | 2025-01-13 | Process check |

### Skip Logic
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IM020 | InvoiceMustBeSkipped | Function | 🟢 | Invoice tables | Low | P3 | 2025-01-13 | 2025-01-13 | Skip logic |
| IM021 | InvoiceIsProcessable | Function | 🟢 | Invoice tables | Low | P3 | 2025-01-13 | 2025-01-13 | Process check |

## 3. Order Processing

### Core Operations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| OP001 | Order_ConvertDepositsIntoPayments | Procedure | 🟢 | Order, Payment tables | High | P1 | 2025-01-13 | 2025-01-13 | Deposit conversion |
| OP002 | Order_InternalProcess | Procedure | 🟢 | Order tables | High | P1 | 2025-01-13 | 2025-01-13 | Order processing |
| OP003 | Order_InternalUpdateBalance | Procedure | 🟢 | Order tables | High | P1 | 2025-01-13 | 2025-01-13 | Balance update |

### Status Functions
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| OP004 | OrderMustBeClosed | Function | 🟢 | Order tables | Low | P2 | 2025-01-13 | 2025-01-13 | Close logic |
| OP005 | OrderMustBeSkipped | Function | 🟢 | Order tables | Low | P2 | 2025-01-13 | 2025-01-13 | Skip logic |
| OP006 | OrderIsProcessable | Function | 🟢 | Order tables | Low | P2 | 2025-01-13 | 2025-01-13 | Process check |

## 4. Inventory Management

### Core Operations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IV001 | InventoryItem_Clone | Procedure | 🟢 | Inventory tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Item cloning |
| IV002 | inventory_adjust_2 | Procedure | 🟢 | Inventory tables | High | P1 | 2025-01-13 | 2025-01-13 | Inventory adjustment |
| IV003 | internal_inventory_transfer | Procedure | 🟢 | Inventory tables | High | P1 | 2025-01-13 | 2025-01-13 | Stock transfer |

### Refresh Operations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IV004 | inventory_refresh | Procedure | 🟢 | Inventory tables | High | P1 | 2025-01-13 | 2025-01-13 | Stock refresh |
| IV005 | inventory_order_refresh | Procedure | 🟢 | Inventory, Order tables | High | P1 | 2025-01-13 | 2025-01-13 | Order stock refresh |
| IV006 | inventory_po_refresh | Procedure | 🟢 | Inventory, PO tables | High | P1 | 2025-01-13 | 2025-01-13 | PO stock refresh |

### Transaction Management
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IV007 | inventory_transaction_add_adjustment | Procedure | 🟢 | Inventory tables | High | P1 | 2025-01-13 | 2025-01-13 | Transaction adjustment |
| IV008 | fix_serial_transactions | Procedure | 🟢 | Inventory tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Serial number fixes |

### Inventory Management Functions
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IM001 | Stock_CalculateStatus | Function | 🟢 | Stock tables | Low | P2 | 2025-01-13 | 2025-01-13 | Status check |
| IM002 | Stock_UpdateLevels | Function | 🟢 | Stock tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Level updates |
| IM003 | Stock_AllocateForOrder | Function | 🟢 | Stock, Order tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Allocation |

## 5. Insurance and Policy Management

### Insurance Operations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IN001 | customer_insurance_fixrank | Procedure | 🟢 | Insurance tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Rank correction |
| IN002 | fixInvoicePolicies | Procedure | 🟢 | Invoice, Insurance tables | High | P2 | 2025-01-13 | 2025-01-13 | Policy fixes |
| IN003 | fixOrderPolicies | Procedure | 🟢 | Order, Insurance tables | High | P2 | 2025-01-13 | 2025-01-13 | Order policy fixes |

### Insurance Functions
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IN001 | Policy_CalculateStatus | Function | 🟢 | Policy tables | Low | P2 | 2025-01-13 | 2025-01-13 | Status check |
| IN002 | Policy_VerificationStatus | Function | 🟢 | Policy tables | Low | P2 | 2025-01-13 | 2025-01-13 | Verify check |
| IN003 | Policy_CalculateCoverage | Function | 🟢 | Policy tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Coverage calc |

## 6. Purchase Orders

### PO Operations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PO001 | PurchaseOrder_UpdateTotals | Procedure | 🟢 | PO tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Total updates |
| PO002 | PurchaseOrder_UpdateTransactions | Procedure | 🟢 | PO, Transaction tables | High | P2 | 2025-01-13 | 2025-01-13 | Transaction updates |

### PO Functions
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PO003 | PO_CalculateStatus | Function | 🟢 | PO tables | Low | P2 | 2025-01-13 | 2025-01-13 | Status check |
| PO004 | PO_ApprovalRequirements | Function | 🟢 | PO tables | Low | P2 | 2025-01-13 | 2025-01-13 | Approval reqs |
| PO005 | PO_UpdateItemStatus | Function | 🟢 | PO tables | Low | P2 | 2025-01-13 | 2025-01-13 | Item updates |
| PO006 | PO_CalculateTotals | Function | 🟢 | PO tables | Low | P2 | 2025-01-13 | 2025-01-13 | Total calc |

## 7. Payment Processing

### Payment Operations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PM001 | Payment_CalculateStatus | Function | 🟢 | Payment tables | Low | P2 | 2025-01-13 | 2025-01-13 | Status check |
| PM002 | Payment_Validate | Function | 🟢 | Payment tables | Low | P2 | 2025-01-13 | 2025-01-13 | Validation |
| PM003 | Payment_CreateTransaction | Function | 🟢 | Payment, Transaction tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Create txn |
| PM004 | Payment_CalculateAllocation | Function | 🟢 | Payment, Invoice tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Allocation |

## 8. Invoice Transactions

### Transaction Operations
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| TR001 | Invoice_Transaction_Process | Function | 🟢 | Invoice, Transaction tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Process txn |
| TR002 | Invoice_Transaction_BeforeInsert | Trigger | 🟢 | Invoice, Transaction tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Before insert |

## 9. Views

### Medical Views
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| MV001 | AbilityEligibilityPayer | View | 🟢 | Payer tables | Low | P2 | 2025-01-13 | 2025-01-13 | Payer view |
| MV002 | Doctor | View | 🟢 | Doctor tables | Low | P2 | 2025-01-13 | 2025-01-13 | Doctor info |
| MV003 | DoctorType | View | 🟢 | Doctor tables | Low | P2 | 2025-01-13 | 2025-01-13 | Doctor types |
| MV004 | ICD10 | View | 🟢 | ICD tables | Low | P2 | 2025-01-13 | 2025-01-13 | ICD-10 codes |
| MV005 | ICD9 | View | 🟢 | ICD tables | Low | P2 | 2025-01-13 | 2025-01-13 | ICD-9 codes |
| MV006 | InsuranceCompany | View | 🟢 | Insurance tables | Low | P2 | 2025-01-13 | 2025-01-13 | Insurance info |
| MV007 | InsuranceCompanyGroup | View | 🟢 | Insurance tables | Low | P2 | 2025-01-13 | 2025-01-13 | Insurance groups |
| MV008 | InsuranceCompanyType | View | 🟢 | Insurance tables | Low | P2 | 2025-01-13 | 2025-01-13 | Insurance types |
| MV009 | ZipCode | View | 🟢 | Location tables | Low | P2 | 2025-01-13 | 2025-01-13 | Zip codes |

### Billing Views
| ID | Name | Type | Status | Dependencies | Complexity | Priority | Start Date | End Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| BV001 | BillingList | View | 🟢 | Order, Insurance tables | Medium | P2 | 2025-01-13 | 2025-01-13 | Billing list |

## Priority Levels
- P1: Critical - Must be completed first
- P2: Important - Should be completed after P1
- P3: Normal - Can be completed after P2
- P4: Low - Can be completed last

## Complexity Levels
- Low: 1-2 days
- Medium: 3-5 days
- High: 5-10 days

## Notes
- Start Date format: YYYY-MM-DD
- End Date format: YYYY-MM-DD
- Dependencies should list all required tables and other procedures
- Status updates should be made daily
- Add notes for any blocking issues or important observations
