# Table: tbl_company

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Address1 | VARCHAR(40) | False |  | None |
| Address2 | VARCHAR(40) | False |  | None |
| BillCustomerCopayUpfront | TINYINT(1) | False | 0 | None |
| City | VARCHAR(25) | False |  | None |
| Fax | VARCHAR(50) | False |  | None |
| FederalTaxID | VARCHAR(9) | False |  | None |
| TaxonomyCode | VARCHAR(20) | False | 332B00000X | None |
| EIN | VARCHAR(20) | False |  | None |
| SSN | VARCHAR(20) | False |  | None |
| TaxIDType | ENUM(SSN, EIN) | False | None | `TaxIDType` ENUM('SSN', 'EIN') NOT NULL |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Name | VARCHAR(50) | False |  | None |
| ParticipatingProvider | TINYINT(1) | False | 0 | None |
| Phone | VARCHAR(50) | False |  | None |
| Phone2 | VARCHAR(50) | False |  | None |
| POAuthorizationCodeReqiered | TINYINT(1) | False | 0 | None |
| Print_PricesOnOrders | TINYINT(1) | False | 0 | None |
| Picture | MEDIUMBLOB | True | None | None |
| POSTypeID | INT(11) | True | 12 | None |
| State | CHAR(2) | False |  | None |
| SystemGenerate_BlanketAssignments | TINYINT(1) | False | 0 | None |
| SystemGenerate_CappedRentalLetters | TINYINT(1) | False | 0 | None |
| SystemGenerate_CustomerAccountNumbers | TINYINT(1) | False | 0 | None |
| SystemGenerate_DeliveryPickupTickets | TINYINT(1) | False | 0 | None |
| SystemGenerate_DroctorsOrder | TINYINT(1) | False | 0 | None |
| SystemGenerate_HIPPAForms | TINYINT(1) | False | 0 | None |
| SystemGenerate_PatientBillOfRights | TINYINT(1) | False | 0 | None |
| SystemGenerate_PurchaseOrderNumber | TINYINT(1) | False | 0 | None |
| WriteoffDifference | TINYINT(1) | False | 0 | None |
| Zip | VARCHAR(10) | False |  | None |
| IncludeLocationInfo | TINYINT(1) | False | 0 | None |
| Contact | VARCHAR(50) | False |  | None |
| Print_CompanyInfoOnInvoice | TINYINT(1) | False | 0 | None |
| Print_CompanyInfoOnDelivery | TINYINT(1) | False | 0 | None |
| Print_CompanyInfoOnPickup | TINYINT(1) | False | 0 | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| Show_InactiveCustomers | TINYINT(1) | False | 0 | None |
| WarehouseID | INT(11) | True | None | None |
| NPI | VARCHAR(10) | True | None | None |
| TaxRateID | INT(11) | True | None | None |
| ImagingServer | VARCHAR(250) | True | None | None |
| ZirmedNumber | VARCHAR(20) | False |  | None |
| AutomaticallyReorderInventory | TINYINT(1) | False | 1 | None |
| AvailityNumber | VARCHAR(50) | False |  | None |
| Show_QuantityOnHand | TINYINT(1) | False | 0 | None |
| Use_Icd10ForNewCmnRx | TINYINT(1) | False | 0 | None |
| OrderSurveyID | INT(11) | True | None | None |
| AbilityIntegrationSettings | MEDIUMTEXT | False | None | None |

## Primary Key
- ID

## Engine
- InnoDB
