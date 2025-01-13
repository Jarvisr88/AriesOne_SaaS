# Table: tbl_invoice

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| CustomerID | INT(11) | False | 0 | None |
| OrderID | INT(11) | True | None | None |
| Approved | TINYINT(1) | False | 0 | None |
| InvoiceDate | DATE | True | None | None |
| SubmittedTo | ENUM(Ins1, Ins2, Ins3, Ins4, Patient) | False | Ins1 | `SubmittedTo` ENUM('Ins1', 'Ins2', 'Ins3', 'Ins4', 'Patient') NOT NULL DEFAULT 'Ins1' |
| SubmittedBy | VARCHAR(50) | True | None | None |
| SubmittedDate | DATE | True | None | None |
| SubmittedBatch | VARCHAR(50) | True | None | None |
| CustomerInsurance1_ID | INT(11) | True | None | None |
| CustomerInsurance2_ID | INT(11) | True | None | None |
| CustomerInsurance3_ID | INT(11) | True | None | None |
| CustomerInsurance4_ID | INT(11) | True | None | None |
| ICD9_1 | VARCHAR(6) | True | None | None |
| ICD9_2 | VARCHAR(6) | True | None | None |
| ICD9_3 | VARCHAR(6) | True | None | None |
| ICD9_4 | VARCHAR(6) | True | None | None |
| DoctorID | INT(11) | True | None | None |
| POSTypeID | INT(11) | True | None | None |
| TaxRateID | INT(11) | True | None | None |
| TaxRatePercent | DOUBLE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| Discount | DOUBLE | True | 0 | None |
| AcceptAssignment | TINYINT(1) | False | 0 | None |
| ClaimNote | VARCHAR(80) | True | None | None |
| FacilityID | INT(11) | True | None | None |
| ReferralID | INT(11) | True | None | None |
| SalesrepID | INT(11) | True | None | None |
| Archived | TINYINT(1) | False | 0 | None |
| ICD10_01 | VARCHAR(8) | True | None | None |
| ICD10_02 | VARCHAR(8) | True | None | None |
| ICD10_03 | VARCHAR(8) | True | None | None |
| ICD10_04 | VARCHAR(8) | True | None | None |
| ICD10_05 | VARCHAR(8) | True | None | None |
| ICD10_06 | VARCHAR(8) | True | None | None |
| ICD10_07 | VARCHAR(8) | True | None | None |
| ICD10_08 | VARCHAR(8) | True | None | None |
| ICD10_09 | VARCHAR(8) | True | None | None |
| ICD10_10 | VARCHAR(8) | True | None | None |
| ICD10_11 | VARCHAR(8) | True | None | None |
| ICD10_12 | VARCHAR(8) | True | None | None |

## Primary Key
- ID

## Foreign Keys
- CustomerID, OrderID → c01.tbl_order (CustomerID, ID)

## Engine
- InnoDB
