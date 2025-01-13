# Table: tbl_manufacturer

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| AccountNumber | VARCHAR(40) | False | None | None |
| Address1 | VARCHAR(40) | False | None | None |
| Address2 | VARCHAR(40) | False | None | None |
| City | VARCHAR(25) | False | None | None |
| Contact | VARCHAR(50) | False | None | None |
| Fax | VARCHAR(50) | False | None | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Name | VARCHAR(50) | False | None | None |
| Phone | VARCHAR(50) | False | None | None |
| Phone2 | VARCHAR(50) | False | None | None |
| State | VARCHAR(2) | False | None | None |
| Zip | VARCHAR(10) | False | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
