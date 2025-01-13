# Table: tbl_paymentplan_payments

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| PaymentPlanID | INT(11) | False | None | None |
| CustomerID | INT(11) | False | None | None |
| Index | INT(11) | False | None | None |
| DueDate | DATE | False | 1900-01-01 | None |
| PaymentDate | DATE | True | None | None |
| Details | MEDIUMTEXT | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
