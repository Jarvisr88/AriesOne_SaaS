# Table: tbl_survey

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Name | VARCHAR(100) | False | None | None |
| Description | VARCHAR(200) | False | None | None |
| Template | MEDIUMTEXT | False | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
