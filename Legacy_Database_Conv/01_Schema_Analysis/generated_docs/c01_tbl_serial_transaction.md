# Table: tbl_serial_transaction

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| TypeID | INT(11) | False | 0 | None |
| SerialID | INT(11) | False | 0 | None |
| TransactionDatetime | DATETIME | False | None | None |
| VendorID | INT(11) | True | None | None |
| WarehouseID | INT(11) | True | None | None |
| CustomerID | INT(11) | True | None | None |
| OrderID | INT(11) | True | None | None |
| OrderDetailsID | INT(11) | True | None | None |
| LotNumber | VARCHAR(50) | False |  | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
