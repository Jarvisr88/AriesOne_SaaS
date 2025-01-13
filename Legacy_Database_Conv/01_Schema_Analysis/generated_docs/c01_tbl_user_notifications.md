# Table: tbl_user_notifications

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Type | VARCHAR(50) | False | None | None |
| Args | VARCHAR(255) | False | None | None |
| UserID | SMALLINT(6) | False | None | None |
| Datetime | TIMESTAMP | False | CURRENT_TIMESTAMP | None |

## Primary Key
- ID

## Engine
- InnoDB
