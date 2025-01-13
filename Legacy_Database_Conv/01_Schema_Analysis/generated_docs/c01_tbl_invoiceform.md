# Table: tbl_invoiceform

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Name | VARCHAR(50) | False | None | None |
| ReportFileName | VARCHAR(50) | False | None | None |
| MarginTop | DOUBLE | False | 0.25 | None |
| MarginLeft | DOUBLE | False | 0.19 | None |
| MarginBottom | DOUBLE | False | 0.18 | None |
| MarginRight | DOUBLE | False | 0.22 | None |
| SpecialCoding | VARCHAR(20) | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
