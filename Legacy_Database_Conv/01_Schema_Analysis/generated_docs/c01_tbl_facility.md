# Table: tbl_facility

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| Address1 | VARCHAR(40) | False | None | None |
| Address2 | VARCHAR(40) | False | None | None |
| City | VARCHAR(25) | False | None | None |
| Contact | VARCHAR(50) | False | None | None |
| DefaultDeliveryWeek | ENUM(1st week of month, 2nd week of month, 3rd week of month, 4th week of month, as needed) | False | None | `DefaultDeliveryWeek` ENUM('1st week of month', '2nd week of month', '3rd week of month', '4th week of month', 'as needed') NOT NULL |
| Directions | LONGTEXT | True | None | None |
| Fax | VARCHAR(50) | False | None | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| MedicaidID | VARCHAR(50) | False | None | None |
| MedicareID | VARCHAR(50) | False | None | None |
| Name | VARCHAR(50) | False | None | None |
| Phone | VARCHAR(50) | False | None | None |
| Phone2 | VARCHAR(50) | False | None | None |
| POSTypeID | INT(11) | True | 12 | None |
| State | VARCHAR(2) | False | None | None |
| Zip | VARCHAR(10) | False | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| NPI | VARCHAR(10) | True | None | None |

## Primary Key
- ID

## Engine
- InnoDB
