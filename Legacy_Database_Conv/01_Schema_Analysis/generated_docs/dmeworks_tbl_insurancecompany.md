# Table: tbl_insurancecompany

**Database:** dmeworks

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Address1 | VARCHAR(40) | False |  | None |
| Address2 | VARCHAR(40) | False |  | None |
| Basis | ENUM(Bill, Allowed) | False | Bill | `Basis` ENUM('Bill', 'Allowed') NOT NULL DEFAULT 'Bill' |
| City | VARCHAR(25) | False |  | None |
| Contact | VARCHAR(50) | False |  | None |
| ECSFormat | ENUM(Region A, Region B, Region C, Region D, Zirmed, Medi-Cal, Availity, Office Ally, Ability) | False | Region | `ECSFormat` ENUM('Region A', 'Region B', 'Region C', 'Region D', 'Zirmed', 'Medi-Cal', 'Availity', 'Office Ally', 'Ability') NOT NULL DEFAULT 'Region A' |
| ExpectedPercent | DOUBLE | True | None | None |
| Fax | VARCHAR(50) | False |  | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Name | VARCHAR(50) | False |  | None |
| Phone | VARCHAR(50) | False |  | None |
| Phone2 | VARCHAR(50) | False |  | None |
| PriceCodeID | INT(11) | True | None | None |
| PrintHAOOnInvoice | TINYINT(1) | True | None | None |
| PrintInvOnInvoice | TINYINT(1) | True | None | None |
| State | CHAR(2) | False |  | None |
| Title | VARCHAR(50) | False |  | None |
| Type | INT(11) | True | None | None |
| Zip | VARCHAR(10) | False |  | None |
| MedicareNumber | VARCHAR(50) | False |  | None |
| OfficeAllyNumber | VARCHAR(50) | False |  | None |
| ZirmedNumber | VARCHAR(50) | False |  | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| InvoiceFormID | INT(11) | True | None | None |
| MedicaidNumber | VARCHAR(50) | False |  | None |
| MIR | SET('MedicareNumber') | False |  | None |
| GroupID | INT(11) | True | None | None |
| AvailityNumber | VARCHAR(50) | False |  | None |
| AbilityNumber | VARCHAR(50) | False |  | None |
| AbilityEligibilityPayerId | INT(11) | True | None | None |

## Primary Key
- ID

## Engine
- InnoDB
