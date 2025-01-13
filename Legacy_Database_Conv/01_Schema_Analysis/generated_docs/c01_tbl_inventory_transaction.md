# Table: tbl_inventory_transaction

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| InventoryItemID | INT(11) | False | 0 | None |
| WarehouseID | INT(11) | False | 0 | None |
| TypeID | INT(11) | False | 0 | None |
| Date | DATE | False | 0000-00-00 | None |
| Quantity | DOUBLE | True | None | None |
| Description | VARCHAR(30) | True | None | None |
| SerialID | INT(11) | True | None | None |
| VendorID | INT(11) | True | None | None |
| CustomerID | INT(11) | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| PurchaseOrderID | INT(11) | True | None | None |
| PurchaseOrderDetailsID | INT(11) | True | None | None |
| InvoiceID | INT(11) | True | None | None |
| ManufacturerID | INT(11) | True | None | None |
| OrderDetailsID | INT(11) | True | None | None |
| OrderID | INT(11) | True | None | None |

## Primary Key
- ID

## Engine
- InnoDB
