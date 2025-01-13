# Table: tbl_inventoryitem

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Barcode | VARCHAR(50) | False |  | None |
| BarcodeType | VARCHAR(50) | False |  | None |
| Basis | ENUM(Bill, Allowed) | False | Bill | `Basis` ENUM('Bill', 'Allowed') NOT NULL DEFAULT 'Bill' |
| CommissionPaidAt | ENUM(Billing, Payment, Never) | False | Billing | `CommissionPaidAt` ENUM('Billing', 'Payment', 'Never') NOT NULL DEFAULT 'Billing' |
| VendorID | INT(11) | True | None | None |
| FlatRate | TINYINT(1) | False | 0 | None |
| FlatRateAmount | DOUBLE | True | None | None |
| Frequency | ENUM(One time, Monthly, Weekly, Never) | False | One | `Frequency` ENUM('One time', 'Monthly', 'Weekly', 'Never') NOT NULL DEFAULT 'One time' |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| InventoryCode | VARCHAR(50) | False |  | None |
| ModelNumber | VARCHAR(50) | False |  | None |
| Name | VARCHAR(100) | False |  | None |
| O2Tank | TINYINT(1) | False | 0 | None |
| Percentage | TINYINT(1) | False | 0 | None |
| PercentageAmount | DOUBLE | False | 0 | None |
| PredefinedTextID | INT(11) | True | None | None |
| ProductTypeID | INT(11) | True | None | None |
| Serialized | TINYINT(1) | False | 0 | None |
| Service | TINYINT(1) | False | 0 | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| Inactive | TINYINT(1) | False | 0 | None |
| ManufacturerID | INT(11) | True | None | None |
| UserField1 | VARCHAR(100) | False |  | None |
| UserField2 | VARCHAR(100) | False |  | None |

## Primary Key
- ID

## Engine
- InnoDB
