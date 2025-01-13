# Table: tbl_referral

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Address1 | VARCHAR(40) | False | None | None |
| Address2 | VARCHAR(40) | False | None | None |
| City | VARCHAR(25) | False | None | None |
| Courtesy | ENUM(Dr., Miss, Mr., Mrs., Rev.) | False | None | `Courtesy` ENUM('Dr.', 'Miss', 'Mr.', 'Mrs.', 'Rev.') NOT NULL |
| Employer | VARCHAR(50) | False | None | None |
| Fax | VARCHAR(50) | False | None | None |
| FirstName | VARCHAR(25) | False | None | None |
| HomePhone | VARCHAR(50) | False | None | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| LastName | VARCHAR(30) | False | None | None |
| MiddleName | VARCHAR(1) | False | None | None |
| Mobile | VARCHAR(50) | False | None | None |
| ReferralTypeID | INT(11) | True | None | None |
| State | VARCHAR(2) | False | None | None |
| Suffix | VARCHAR(4) | False | None | None |
| WorkPhone | VARCHAR(50) | False | None | None |
| Zip | VARCHAR(10) | False | None | None |
| LastContacted | DATE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
