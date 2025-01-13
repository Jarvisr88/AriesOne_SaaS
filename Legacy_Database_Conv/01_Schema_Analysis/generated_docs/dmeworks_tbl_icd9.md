# Table: tbl_icd9

**Database:** dmeworks

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Code | VARCHAR(6) | False |  | None |
| Description | VARCHAR(255) | False |  | None |
| ActiveDate | DATE | True | None | None |
| InactiveDate | DATE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- Code

## Engine
- InnoDB
