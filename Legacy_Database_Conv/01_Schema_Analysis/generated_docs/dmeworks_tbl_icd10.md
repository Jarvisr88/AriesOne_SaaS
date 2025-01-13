# Table: tbl_icd10

**Database:** dmeworks

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Code | VARCHAR(8) | False | None | None |
| Description | VARCHAR(255) | False |  | None |
| Header | TINYINT(1) | False | 0 | None |
| ActiveDate | DATE | True | None | None |
| InactiveDate | DATE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- Code

## Engine
- InnoDB
