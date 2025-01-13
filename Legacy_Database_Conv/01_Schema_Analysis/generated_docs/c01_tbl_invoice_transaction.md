# Table: tbl_invoice_transaction

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| InvoiceDetailsID | INT(11) | False | 0 | None |
| InvoiceID | INT(11) | False | 0 | None |
| CustomerID | INT(11) | False | 0 | None |
| InsuranceCompanyID | INT(11) | True | None | None |
| CustomerInsuranceID | INT(11) | True | None | None |
| TransactionTypeID | INT(11) | False | 0 | None |
| TransactionDate | DATE | True | None | None |
| Quantity | DOUBLE | False | 0 | None |
| BatchNumber | VARCHAR(20) | False |  | None |
| Comments | TEXT | True | None | None |
| Extra | TEXT | True | None | None |
| Approved | TINYINT(1) | False | 0 | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Foreign Keys
- CustomerID, InvoiceID, InvoiceDetailsID → c01.tbl_invoicedetails (CustomerID, InvoiceID, ID)

## Engine
- InnoDB
