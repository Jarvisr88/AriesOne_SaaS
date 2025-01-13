# Table: tbl_invoicenotes

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| InvoiceDetailsID | INT(11) | False | 0 | None |
| InvoiceID | INT(11) | False | 0 | None |
| CustomerID | INT(11) | False | 0 | None |
| CallbackDate | DATE | True | None | None |
| Done | TINYINT(1) | False | 0 | None |
| Notes | LONGTEXT | False | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
