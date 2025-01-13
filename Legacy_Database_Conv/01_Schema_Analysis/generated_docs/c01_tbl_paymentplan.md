# Table: tbl_paymentplan

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| CustomerID | INT(11) | False | None | None |
| Period | ENUM(Weekly, Bi-weekly, Monthly) | False | Weekly | `Period` ENUM('Weekly', 'Bi-weekly', 'Monthly') NOT NULL DEFAULT 'Weekly' |
| FirstPayment | DATE | False | 1900-01-01 | None |
| PaymentCount | INT(11) | False | None | None |
| Details | MEDIUMTEXT | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
