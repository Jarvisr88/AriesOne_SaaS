# Table: tbl_location

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Contact | VARCHAR(50) | False |  | None |
| Name | VARCHAR(50) | False |  | None |
| Code | VARCHAR(40) | False |  | None |
| City | VARCHAR(25) | False |  | None |
| Address1 | VARCHAR(40) | False |  | None |
| Address2 | VARCHAR(40) | False |  | None |
| State | CHAR(2) | False |  | None |
| Zip | VARCHAR(10) | False |  | None |
| Fax | VARCHAR(50) | False |  | None |
| FEDTaxID | VARCHAR(50) | False |  | None |
| TaxIDType | ENUM(SSN, EIN) | False | SSN | `TaxIDType` ENUM('SSN', 'EIN') NOT NULL DEFAULT 'SSN' |
| Phone | VARCHAR(50) | False |  | None |
| Phone2 | VARCHAR(50) | False |  | None |
| PrintInfoOnDelPupTicket | TINYINT(1) | True | None | None |
| PrintInfoOnInvoiceAcctStatements | TINYINT(1) | True | None | None |
| PrintInfoOnPartProvider | TINYINT(1) | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| NPI | VARCHAR(10) | True | None | None |
| InvoiceFormID | INT(11) | True | None | None |
| PriceCodeID | INT(11) | True | None | None |
| ParticipatingProvider | TINYINT(1) | True | None | None |
| Email | VARCHAR(50) | True | None | None |
| WarehouseID | INT(11) | True | None | None |
| POSTypeID | INT(11) | True | 12 | None |
| TaxRateID | INT(11) | True | None | None |

## Primary Key
- ID

## Engine
- InnoDB
