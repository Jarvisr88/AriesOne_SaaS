# Table: tbl_image

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Name | VARCHAR(50) | False |  | None |
| Type | VARCHAR(50) | False |  | None |
| Description | TEXT | True | None | None |
| CustomerID | INT(11) | True | None | None |
| OrderID | INT(11) | True | None | None |
| InvoiceID | INT(11) | True | None | None |
| DoctorID | INT(11) | True | None | None |
| CMNFormID | INT(11) | True | None | None |
| Thumbnail | BLOB | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
