# Table: tbl_warehouse

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Address1 | VARCHAR(40) | False |  | None |
| Address2 | VARCHAR(40) | False |  | None |
| City | VARCHAR(25) | False |  | None |
| Contact | VARCHAR(50) | False |  | None |
| Fax | VARCHAR(50) | False |  | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Name | VARCHAR(50) | False |  | None |
| Phone | VARCHAR(50) | False |  | None |
| Phone2 | VARCHAR(50) | False |  | None |
| State | CHAR(2) | False |  | None |
| Zip | VARCHAR(10) | False |  | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
