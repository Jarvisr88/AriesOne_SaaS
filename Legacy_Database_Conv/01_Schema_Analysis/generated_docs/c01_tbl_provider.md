# Table: tbl_provider

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| LocationID | INT(11) | False | 0 | None |
| InsuranceCompanyID | INT(11) | False | 0 | None |
| ProviderNumber | VARCHAR(25) | False |  | None |
| Password | VARCHAR(20) | False |  | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| ProviderNumberType | VARCHAR(6) | False | 1C | None |

## Primary Key
- ID

## Engine
- InnoDB
