# Table: tbl_doctor

**Database:** dmeworks

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Address1 | VARCHAR(40) | False | None | None |
| Address2 | VARCHAR(40) | False | None | None |
| City | VARCHAR(25) | False | None | None |
| Contact | VARCHAR(50) | False | None | None |
| Courtesy | ENUM(Dr., Miss, Mr., Mrs., Rev.) | False | None | `Courtesy` ENUM('Dr.', 'Miss', 'Mr.', 'Mrs.', 'Rev.') NOT NULL |
| Fax | VARCHAR(50) | False | None | None |
| FirstName | VARCHAR(25) | False | None | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| LastName | VARCHAR(30) | False | None | None |
| LicenseNumber | VARCHAR(16) | False | None | None |
| LicenseExpired | DATE | True | None | None |
| MedicaidNumber | VARCHAR(16) | False | None | None |
| MiddleName | VARCHAR(1) | False | None | None |
| OtherID | VARCHAR(16) | False | None | None |
| FEDTaxID | VARCHAR(9) | False |  | None |
| DEANumber | VARCHAR(20) | False |  | None |
| Phone | VARCHAR(50) | False | None | None |
| Phone2 | VARCHAR(50) | False | None | None |
| State | VARCHAR(2) | False | None | None |
| Suffix | VARCHAR(4) | False | None | None |
| Title | VARCHAR(50) | False | None | None |
| TypeID | INT(11) | True | None | None |
| UPINNumber | VARCHAR(11) | False | None | None |
| Zip | VARCHAR(10) | False | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| NPI | VARCHAR(10) | True | None | None |
| PecosEnrolled | TINYINT(1) | False | 0 | None |

## Primary Key
- ID

## Engine
- InnoDB
