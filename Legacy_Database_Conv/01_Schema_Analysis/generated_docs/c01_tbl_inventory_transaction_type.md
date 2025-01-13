# Table: tbl_inventory_transaction_type

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Name | VARCHAR(50) | False |  | None |
| OnHand | INT(11) | False | 0 | None |
| Committed | INT(11) | False | 0 | None |
| OnOrder | INT(11) | False | 0 | None |
| UnAvailable | INT(11) | False | 0 | None |
| Rented | INT(11) | False | 0 | None |
| Sold | INT(11) | False | 0 | None |
| BackOrdered | INT(11) | False | 0 | None |
| AdjTotalCost | INT(11) | False | 0 | None |

## Primary Key
- ID

## Engine
- InnoDB
