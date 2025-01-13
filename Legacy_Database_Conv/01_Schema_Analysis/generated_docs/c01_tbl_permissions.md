# Table: tbl_permissions

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| UserID | SMALLINT(6) | False | None | None |
| ObjectID | SMALLINT(6) | False | None | None |
| ADD_EDIT | TINYINT(1) | False | 0 | None |
| DELETE | TINYINT(1) | False | 0 | None |
| PROCESS | TINYINT(1) | False | 0 | None |
| VIEW | TINYINT(1) | False | 0 | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- UserID, ObjectID

## Engine
- InnoDB
