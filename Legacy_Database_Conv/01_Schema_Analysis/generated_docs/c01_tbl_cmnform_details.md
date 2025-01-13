# Table: tbl_cmnform_details

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| BillingCode | VARCHAR(50) | True | None | None |
| InventoryItemID | INT(11) | False | 0 | None |
| OrderedQuantity | DOUBLE | False | 0 | None |
| OrderedUnits | VARCHAR(50) | True | None | None |
| BillablePrice | DOUBLE | False | 0 | None |
| AllowablePrice | DOUBLE | False | 0 | None |
| Period | ENUM(One time, Daily, Weekly, Monthly, Quarterly, Semi-Annually, Annually, Custom) | False | One | `Period` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Semi-Annually', 'Annually', 'Custom') NOT NULL DEFAULT 'One time' |
| Modifier1 | VARCHAR(8) | False |  | None |
| Modifier2 | VARCHAR(8) | False |  | None |
| Modifier3 | VARCHAR(8) | False |  | None |
| Modifier4 | VARCHAR(8) | False |  | None |
| PredefinedTextID | INT(11) | True | None | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |

## Primary Key
- ID

## Engine
- InnoDB
