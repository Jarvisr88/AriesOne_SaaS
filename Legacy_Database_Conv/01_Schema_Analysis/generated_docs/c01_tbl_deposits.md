# Table: tbl_deposits

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CustomerID | INT(11) | False | None | None |
| OrderID | INT(11) | False | None | None |
| Date | DATE | False | None | None |
| PaymentMethod | ENUM(Cash, Check, Credit Card) | False | None | `PaymentMethod` ENUM('Cash', 'Check', 'Credit Card') NOT NULL |
| Notes | TEXT | False | None | None |
| LastUpdateUserID | SMALLINT(6) | False | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- CustomerID, OrderID

## Foreign Keys
- CustomerID, OrderID → c01.tbl_order (CustomerID, ID)

## Engine
- InnoDB
