# Table: tbl_orderdeposits

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| OrderDetailsID | INT(11) | False | None | None |
| OrderID | INT(11) | False | None | None |
| CustomerID | INT(11) | False | None | None |
| Date | DATE | False | None | None |
| LastUpdateUserID | SMALLINT(6) | False | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- OrderDetailsID

## Foreign Keys
- CustomerID, OrderID → c01.tbl_order (CustomerID, ID)
- OrderDetailsID → c01.tbl_orderdetails (ID)

## Engine
- InnoDB
