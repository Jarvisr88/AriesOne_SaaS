# Table: tbl_submitter

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| ECSFormat | ENUM(Region A, Region B, Region C, Region D) | True | NULL | `ECSFormat` ENUM('Region A', 'Region B', 'Region C', 'Region D') NULL DEFAULT NULL |
| Name | VARCHAR(50) | False |  | None |
| Number | VARCHAR(16) | False |  | None |
| Password | VARCHAR(50) | False |  | None |
| Production | TINYINT(1) | False | 0 | None |
| ContactName | VARCHAR(50) | False |  | None |
| Address1 | VARCHAR(40) | False |  | None |
| Address2 | VARCHAR(40) | False |  | None |
| City | VARCHAR(25) | False |  | None |
| State | CHAR(2) | False |  | None |
| Zip | VARCHAR(10) | False |  | None |
| Phone1 | VARCHAR(50) | False |  | None |
| LastBatchNumber | VARCHAR(50) | False |  | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
