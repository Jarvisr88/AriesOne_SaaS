# Table: tbl_changes

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| TableName | VARCHAR(64) | False | None | None |
| SessionID | INT(11) | False | None | None |
| LastUpdateUserID | SMALLINT(6) | False | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- TableName

## Engine
- InnoDB
