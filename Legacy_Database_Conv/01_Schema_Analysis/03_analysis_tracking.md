# Schema Analysis Tracking

## Total Object Count

### Database Objects
- Tables: 119
- Views: 24
- Stored Procedures: 56
- Functions: 22
- Triggers: 1
- Total Objects: 222

## Analysis Progress

### Database: c01 (Primary Database)

#### Tables (92 total)
- [ ] tbl_ability_eligibility_request
- [ ] tbl_authorizationtype
- [ ] tbl_batchpayment
- [ ] tbl_billingtype
- [ ] tbl_changes
- [ ] tbl_cmnform
- [ ] tbl_cmnform_0102a
- [ ] tbl_cmnform_0102b
- [ ] tbl_cmnform_0203a
- [ ] tbl_cmnform_0203b
- [ ] tbl_cmnform_0302
- [ ] tbl_cmnform_0403b
- [ ] tbl_cmnform_0403c
- [ ] tbl_cmnform_0602b
- [ ] tbl_cmnform_0702a
- [ ] tbl_cmnform_0702b
- [ ] tbl_cmnform_0802
- [ ] tbl_cmnform_0902
- [ ] tbl_cmnform_1002a
- [ ] tbl_cmnform_1002b
- [ ] tbl_cmnform_4842
- [ ] tbl_cmnform_48403
- [ ] tbl_cmnform_drorder
- [ ] tbl_cmnform_uro
- [ ] tbl_company
- [x] tbl_customer
- [ ] tbl_customer_insurance
- [ ] tbl_customer_note
- [ ] tbl_customer_payment
- [ ] tbl_customer_payment_detail
- [ ] tbl_doctor
- [ ] tbl_doctor_group
- [ ] tbl_doctor_insurance
- [ ] tbl_facility
- [ ] tbl_facility_insurance
- [ ] tbl_icd9
- [ ] tbl_icd10
- [ ] tbl_insurance_company
- [ ] tbl_insurance_company_note
- [ ] tbl_insurance_coverage
- [ ] tbl_insurance_coverage_detail
- [ ] tbl_insurance_modifier
- [ ] tbl_insurance_payment
- [ ] tbl_insurance_payment_detail
- [ ] tbl_insurance_plan
- [ ] tbl_insurance_plan_coverage
- [ ] tbl_insurance_plan_modifier
- [ ] tbl_insurance_type
- [ ] tbl_inventory
- [ ] tbl_inventory_item
- [ ] tbl_inventory_location
- [ ] tbl_inventory_transaction
- [ ] tbl_invoice
- [ ] tbl_invoice_detail
- [ ] tbl_invoice_payment
- [ ] tbl_invoice_transaction
- [ ] tbl_invoice_transaction_type
- [ ] tbl_location
- [x] tbl_order
- [x] tbl_orderdetails
- [ ] tbl_payer
- [ ] tbl_payment
- [ ] tbl_payment_detail
- [ ] tbl_payment_type
- [ ] tbl_price
- [ ] tbl_price_code
- [ ] tbl_price_level
- [ ] tbl_referral
- [ ] tbl_referral_type
- [ ] tbl_serial
- [ ] tbl_serial_transaction
- [ ] tbl_tax
- [ ] tbl_tax_rate
- [ ] tbl_user
- [ ] tbl_user_group
- [ ] tbl_user_permission
- [ ] tbl_warehouse

#### Views (24 total)
- [ ] view_customer
- [ ] view_customer_insurance
- [ ] view_doctor
- [ ] view_facility
- [ ] view_insurance_company
- [ ] view_inventory
- [ ] view_invoice
- [ ] view_order
- [ ] view_payment
- [ ] view_referral
- [ ] view_orderdetails
- [ ] view_orderdetails_core
- [ ] view_customer_insurance_coverage
- [ ] view_doctor_insurance
- [ ] view_facility_insurance
- [ ] view_insurance_coverage
- [ ] view_insurance_plan
- [ ] view_insurance_plan_coverage
- [ ] view_insurance_plan_modifier
- [ ] view_insurance_type
- [ ] view_inventory_item
- [ ] view_inventory_location
- [ ] view_inventory_transaction
- [ ] view_invoice_detail
- [ ] view_invoice_payment

#### Stored Procedures (56 total)
- [ ] InvoiceDetails_AddAutoSubmit
- [ ] InvoiceDetails_AddPayment
- [ ] InvoiceDetails_InternalAddSubmitted
- [ ] InvoiceDetails_RecalculateInternals
- [ ] sp_add_customer
- [ ] sp_add_doctor
- [ ] sp_add_facility
- [ ] sp_add_insurance_company
- [ ] sp_add_insurance_coverage
- [ ] sp_add_insurance_modifier
- [ ] sp_add_insurance_payment
- [ ] sp_add_insurance_plan
- [ ] sp_add_insurance_plan_coverage
- [ ] sp_add_insurance_plan_modifier
- [ ] sp_add_insurance_type
- [ ] sp_add_inventory
- [ ] sp_add_inventory_item
- [ ] sp_add_inventory_location
- [ ] sp_add_inventory_transaction
- [ ] sp_add_invoice
- [ ] sp_add_invoice_detail
- [ ] sp_add_invoice_payment
- [ ] sp_add_invoice_transaction
- [ ] sp_add_invoice_transaction_type
- [ ] sp_add_location
- [ ] sp_add_order
- [ ] sp_add_orderdetails
- [ ] sp_add_payer
- [ ] sp_add_payment
- [ ] sp_add_payment_detail
- [ ] sp_add_payment_type
- [ ] sp_add_price
- [ ] sp_add_price_code
- [ ] sp_add_price_level
- [ ] sp_add_referral
- [ ] sp_add_referral_type
- [ ] sp_add_serial
- [ ] sp_add_serial_transaction
- [ ] sp_add_tax
- [ ] sp_add_tax_rate
- [ ] sp_add_user
- [ ] sp_add_user_group
- [ ] sp_add_user_permission
- [ ] sp_add_warehouse
- [ ] sp_update_customer
- [ ] sp_update_doctor
- [ ] sp_update_facility
- [ ] sp_update_insurance_company
- [ ] sp_update_insurance_coverage
- [ ] sp_update_insurance_modifier
- [ ] sp_update_insurance_payment
- [ ] sp_update_insurance_plan
- [ ] sp_update_insurance_plan_coverage
- [ ] sp_update_insurance_plan_modifier
- [ ] sp_update_insurance_type
- [ ] sp_update_inventory
- [ ] sp_update_inventory_item
- [ ] sp_update_inventory_location
- [ ] sp_update_inventory_transaction
- [ ] sp_update_invoice
- [ ] sp_update_invoice_detail
- [ ] sp_update_invoice_payment
- [ ] sp_update_invoice_transaction
- [ ] sp_update_invoice_transaction_type
- [ ] sp_update_location
- [ ] sp_update_order
- [ ] sp_update_orderdetails
- [ ] sp_update_payer
- [ ] sp_update_payment
- [ ] sp_update_payment_detail
- [ ] sp_update_payment_type
- [ ] sp_update_price
- [ ] sp_update_price_code
- [ ] sp_update_price_level
- [ ] sp_update_referral
- [ ] sp_update_referral_type
- [ ] sp_update_serial
- [ ] sp_update_serial_transaction
- [ ] sp_update_tax
- [ ] sp_update_tax_rate
- [ ] sp_update_user
- [ ] sp_update_user_group
- [ ] sp_update_user_permission
- [ ] sp_update_warehouse

#### Functions (22 total)
- [ ] GetAllowableAmount
- [ ] GetQuantityMultiplier
- [ ] GetCustomerName
- [ ] GetDoctorName
- [ ] GetFacilityName
- [ ] GetInsuranceCompanyName
- [ ] GetInsuranceCoverage
- [ ] GetInsuranceModifier
- [ ] GetInsurancePayment
- [ ] GetInsurancePlan
- [ ] GetInsurancePlanCoverage
- [ ] GetInsurancePlanModifier
- [ ] GetInsuranceType
- [ ] GetInventoryItem
- [ ] GetInventoryLocation
- [ ] GetInventoryTransaction
- [ ] GetInvoiceDetail
- [ ] GetInvoicePayment
- [ ] GetInvoiceTransaction
- [ ] GetInvoiceTransactionType
- [ ] GetLocation
- [ ] GetOrder
- [ ] GetOrderdetails
- [ ] GetPayer
- [ ] GetPayment
- [ ] GetPaymentDetail
- [ ] GetPaymentType
- [ ] GetPrice
- [ ] GetPriceCode
- [ ] GetPriceLevel
- [ ] GetReferral
- [ ] GetReferralType
- [ ] GetSerial
- [ ] GetSerialTransaction
- [ ] GetTax
- [ ] GetTaxRate
- [ ] GetUser
- [ ] GetUserGroup
- [ ] GetUserPermission
- [ ] GetWarehouse

#### Triggers (1 total)
- [ ] tr_update_invoice

### Database: repository (8 total)
- [ ] tbl_batches
- [ ] tbl_batch_detail
- [ ] tbl_batch_status
- [ ] tbl_batch_type
- [ ] tbl_workflow
- [ ] tbl_workflow_step
- [ ] view_batches
- [ ] view_batch_detail

### Database: dmeworks (19 total)
- [ ] tbl_doctor
- [ ] tbl_doctor_group
- [ ] tbl_facility
- [ ] tbl_insurance_company
- [ ] tbl_location
- [ ] tbl_referral
- [ ] tbl_user
- [ ] tbl_warehouse
- [ ] view_doctor
- [ ] view_facility
- [ ] view_insurance_company
- [ ] view_location
- [ ] view_referral
- [ ] view_user
- [ ] view_warehouse
- [ ] sp_add_doctor
- [ ] sp_add_facility
- [ ] sp_add_insurance_company
- [ ] sp_add_location
- [ ] sp_add_referral
- [ ] sp_add_user
- [ ] sp_add_warehouse

## Analysis Status
- Total Objects to Analyze: 222
- Analyzed: 3
- Remaining: 219
- Progress: 1.4%

## Analysis Priorities
1. Tables (119)
2. Views (24)
3. Stored Procedures (56)
4. Functions (22)
5. Triggers (1)

## Next Steps
1. Complete detailed analysis of remaining tables
2. Document all view definitions
3. Analyze stored procedures
4. Analyze functions
5. Document trigger logic
6. Map all dependencies
7. Create complete data dictionary
