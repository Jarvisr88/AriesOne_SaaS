# Table: tbl_order

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| CustomerID | INT(11) | False | 0 | None |
| Approved | TINYINT(1) | False | 0 | None |
| RetailSales | TINYINT(1) | False | 0 | None |
| OrderDate | DATE | True | None | None |
| DeliveryDate | DATE | True | None | None |
| BillDate | DATE | True | None | None |
| EndDate | DATE | True | None | None |
| ShippingMethodID | INT(11) | True | None | None |
| SpecialInstructions | TEXT | True | None | None |
| TicketMesage | VARCHAR(50) | True | None | None |
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
| TakenBy | VARCHAR(50) | True |  | None |
| Discount | DOUBLE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| SaleType | ENUM(Retail, Back Office) | False | Back | `SaleType` ENUM('Retail', 'Back Office') NOT NULL DEFAULT 'Back Office' |
| State | ENUM(New, Approved, Closed, Canceled) | False | New | `State` ENUM('New', 'Approved', 'Closed', 'Canceled') NOT NULL DEFAULT 'New' |
| AcceptAssignment | TINYINT(1) | False | 0 | None |
| ClaimNote | VARCHAR(80) | True | None | None |
| FacilityID | INT(11) | True | None | None |
| ReferralID | INT(11) | True | None | None |
| SalesrepID | INT(11) | True | None | None |
| LocationID | INT(11) | True | None | None |
| Archived | TINYINT(1) | False | 0 | None |
| TakenAt | DATETIME | True | None | None |
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
| UserField1 | VARCHAR(100) | False |  | None |
| UserField2 | VARCHAR(100) | False |  | None |

## Primary Key
- ID

## Engine
- InnoDB
