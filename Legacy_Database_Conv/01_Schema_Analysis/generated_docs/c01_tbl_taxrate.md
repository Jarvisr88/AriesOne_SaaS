# Table: tbl_taxrate

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| CityTax | DOUBLE | True | None | None |
| CountyTax | DOUBLE | True | None | None |
| Name | VARCHAR(50) | False | None | None |
| OtherTax | DOUBLE | True | None | None |
| StateTax | DOUBLE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
