# Table: tbl_invoicedetails

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| InvoiceID | INT(11) | False | 0 | None |
| CustomerID | INT(11) | False | 0 | None |
| InventoryItemID | INT(11) | False | 0 | None |
| PriceCodeID | INT(11) | False | 0 | None |
| OrderID | INT(11) | True | None | None |
| OrderDetailsID | INT(11) | True | None | None |
| Quantity | DOUBLE | False | 0 | None |
| InvoiceDate | DATE | True | None | None |
| DOSFrom | DATE | False | 0000-00-00 | None |
| DOSTo | DATE | True | None | None |
| BillingCode | VARCHAR(50) | True | None | None |
| Modifier1 | VARCHAR(8) | False |  | None |
| Modifier2 | VARCHAR(8) | False |  | None |
| Modifier3 | VARCHAR(8) | False |  | None |
| Modifier4 | VARCHAR(8) | False |  | None |
| DXPointer | VARCHAR(50) | True | None | None |
| BillingMonth | INT(11) | False | 0 | None |
| SendCMN_RX_w_invoice | TINYINT(1) | False | 0 | None |
| SpecialCode | VARCHAR(50) | True | None | None |
| ReviewCode | VARCHAR(50) | True | None | None |
| MedicallyUnnecessary | TINYINT(1) | False | 0 | None |
| AuthorizationNumber | VARCHAR(50) | True | None | None |
| AuthorizationTypeID | INT(11) | True | None | None |
| InvoiceNotes | VARCHAR(255) | True | None | None |
| InvoiceRecord | VARCHAR(255) | True | None | None |
| CMNFormID | INT(11) | True | None | None |
| HAOCode | VARCHAR(10) | True | None | None |
| BillIns1 | TINYINT(1) | False | 1 | None |
| BillIns2 | TINYINT(1) | False | 1 | None |
| BillIns3 | TINYINT(1) | False | 1 | None |
| BillIns4 | TINYINT(1) | False | 1 | None |
| Hardship | TINYINT(1) | False | 0 | None |
| ShowSpanDates | TINYINT(1) | False | 0 | None |
| CurrentPayer | ENUM(Ins1, Ins2, Ins3, Ins4, Patient, None) | False | Ins1 | `CurrentPayer` ENUM('Ins1', 'Ins2', 'Ins3', 'Ins4', 'Patient', 'None') NOT NULL DEFAULT 'Ins1' |
| Pendings | TINYINT(4) | False | 0 | None |
| Submits | TINYINT(4) | False | 0 | None |
| Payments | TINYINT(4) | False | 0 | None |
| SubmittedDate | DATE | True | None | None |
| Submitted | TINYINT(1) | False | 0 | None |
| CurrentInsuranceCompanyID | INT(11) | True | None | None |
| CurrentCustomerInsuranceID | INT(11) | True | None | None |
| AcceptAssignment | TINYINT(1) | False | 0 | None |
| DrugNoteField | VARCHAR(20) | True | None | None |
| DrugControlNumber | VARCHAR(50) | True | None | None |
| NopayIns1 | TINYINT(1) | False | 0 | None |
| PointerICD10 | SMALLINT(6) | False | 0 | None |
| DXPointer10 | VARCHAR(50) | True | None | None |
| HaoDescription | VARCHAR(100) | True | None | None |

## Primary Key
- ID

## Foreign Keys
- CustomerID, InvoiceID → c01.tbl_invoice (CustomerID, ID)

## Engine
- InnoDB
