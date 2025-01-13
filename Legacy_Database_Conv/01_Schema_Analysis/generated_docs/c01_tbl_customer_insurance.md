# Table: tbl_customer_insurance

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Address1 | VARCHAR(40) | False |  | None |
| Address2 | VARCHAR(40) | False |  | None |
| City | VARCHAR(25) | False |  | None |
| State | CHAR(2) | False |  | None |
| Zip | VARCHAR(10) | False |  | None |
| Basis | ENUM(Bill, Allowed) | False | Bill | `Basis` ENUM('Bill', 'Allowed') NOT NULL DEFAULT 'Bill' |
| CustomerID | INT(11) | False | 0 | None |
| DateofBirth | DATE | True | None | None |
| Gender | ENUM(Male, Female) | False | Male | `Gender` ENUM('Male', 'Female') NOT NULL DEFAULT 'Male' |
| GroupNumber | VARCHAR(50) | False |  | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| InactiveDate | DATE | True | None | None |
| InsuranceCompanyID | INT(11) | False | 0 | None |
| InsuranceType | CHAR(2) | True | None | None |
| FirstName | VARCHAR(25) | False |  | None |
| LastName | VARCHAR(30) | False |  | None |
| MiddleName | CHAR(1) | False |  | None |
| Employer | VARCHAR(50) | False |  | None |
| Mobile | VARCHAR(50) | False |  | None |
| PaymentPercent | INT(11) | True | None | None |
| Phone | VARCHAR(50) | False |  | None |
| PolicyNumber | VARCHAR(50) | False |  | None |
| Rank | INT(11) | True | None | None |
| RelationshipCode | CHAR(2) | True | None | None |
| RequestEligibility | TINYINT(1) | False | 0 | None |
| RequestEligibilityOn | DATE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| Suffix | VARCHAR(4) | False |  | None |

## Primary Key
- ID

## Engine
- InnoDB
