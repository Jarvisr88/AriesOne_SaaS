# Table: tbl_purchaseorderdetails

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| BackOrder | INT(11) | False | 0 | None |
| Ordered | INT(11) | False | 0 | None |
| Received | INT(11) | False | 0 | None |
| Price | DOUBLE | False | 0 | None |
| Customer | VARCHAR(50) | True | None | None |
| DatePromised | DATE | True | None | None |
| DateReceived | DATE | True | None | None |
| DropShipToCustomer | TINYINT(1) | False | 0 | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| InventoryItemID | INT(11) | False | None | None |
| PurchaseOrderID | INT(11) | True | None | None |
| WarehouseID | INT(11) | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| VendorSTKNumber | VARCHAR(50) | True | None | None |
| ReferenceNumber | VARCHAR(50) | True | None | None |

## Primary Key
- ID

## Engine
- InnoDB
