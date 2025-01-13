# Table: tbl_inventory

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| WarehouseID | INT(11) | False | 0 | None |
| InventoryItemID | INT(11) | False | 0 | None |
| OnHand | DOUBLE | False | 0 | None |
| Committed | DOUBLE | False | 0 | None |
| OnOrder | DOUBLE | False | 0 | None |
| UnAvailable | DOUBLE | False | 0 | None |
| Rented | DOUBLE | False | 0 | None |
| Sold | DOUBLE | False | 0 | None |
| BackOrdered | DOUBLE | False | 0 | None |
| ReOrderPoint | DOUBLE | False | 0 | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- WarehouseID, InventoryItemID

## Engine
- InnoDB
