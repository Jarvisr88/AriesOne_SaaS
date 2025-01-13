# Database Objects Analysis

## Database: c01

### Tables
1. tbl_ability_eligibility_request
2. tbl_authorizationtype
3. tbl_batchpayment
4. tbl_billingtype
5. tbl_changes
6. tbl_cmnform
7. tbl_cmnform_0102a
8. tbl_cmnform_0102b
9. tbl_cmnform_0203a
10. tbl_cmnform_0203b
11. tbl_company
12. tbl_customer
13. tbl_order
14. tbl_orderdetails
15. tbl_insurancetype
16. tbl_inventoryitem
17. tbl_invoicedetails
18. tbl_invoice_transactiontype
19. tbl_location
20. tbl_payer
21. tbl_referraltype
22. tbl_serial_transaction
23. tbl_taxrate

### Views
1. tbl_icd10
2. view_orderdetails
3. view_orderdetails_core

### Stored Procedures
1. InvoiceDetails_AddAutoSubmit
2. InvoiceDetails_AddPayment
3. InvoiceDetails_InternalAddSubmitted
4. InvoiceDetails_RecalculateInternals

### Functions
1. GetAllowableAmount
2. GetQuantityMultiplier

## Database: repository

### Tables
1. tbl_batches

## Database: dmeworks

### Tables
1. tbl_doctor
2. tbl_insurancecompany

## Analysis Approach

For each object, we will document:

1. **Tables**
   - Full schema definition
   - Column details
   - Constraints
   - Indexes
   - Relationships
   - Data patterns

2. **Views**
   - View definition
   - Dependencies
   - Usage patterns
   - Performance considerations

3. **Stored Procedures**
   - Full procedure code
   - Parameters
   - Business logic
   - Dependencies
   - Error handling

4. **Functions**
   - Function definition
   - Parameters
   - Return values
   - Usage context
   - Dependencies

## Analysis Order

1. Core Tables (Customer, Order, Inventory)
2. Supporting Tables (Types, Locations)
3. Transaction Tables (Invoice, Payment)
4. Medical Tables (CMN Forms)
5. Views
6. Stored Procedures
7. Functions
