# Table: tbl_user

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | SMALLINT(6) | False | None | AUTO_INCREMENT |
| Login | VARCHAR(16) | False | None | None |
| Password | VARCHAR(32) | False | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| Email | VARCHAR(150) | False |  | None |

## Primary Key
- ID

## Engine
- InnoDB
