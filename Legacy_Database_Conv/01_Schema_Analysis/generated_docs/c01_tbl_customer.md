# Table: tbl_customer

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| AccountNumber | VARCHAR(40) | False |  | None |
| Address1 | VARCHAR(40) | False |  | None |
| Address2 | VARCHAR(40) | False |  | None |
| BillingTypeID | INT(11) | True | None | None |
| City | VARCHAR(25) | False |  | None |
| Courtesy | ENUM(Dr., Miss, Mr., Mrs., Rev.) | False | Dr. | `Courtesy` ENUM('Dr.', 'Miss', 'Mr.', 'Mrs.', 'Rev.') NOT NULL DEFAULT 'Dr.' |
| CustomerBalance | DOUBLE | True | None | None |
| CustomerClassCode | CHAR(2) | True | None | None |
| CustomerTypeID | INT(11) | True | None | None |
| DeceasedDate | DATE | True | None | None |
| DateofBirth | DATE | True | None | None |
| FirstName | VARCHAR(25) | False |  | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| LastName | VARCHAR(30) | False |  | None |
| LocationID | INT(11) | True | None | None |
| MiddleName | CHAR(1) | False |  | None |
| Phone | VARCHAR(50) | False |  | None |
| Phone2 | VARCHAR(50) | False |  | None |
| State | CHAR(2) | False |  | None |
| Suffix | VARCHAR(4) | False |  | None |
| TotalBalance | DOUBLE | True | None | None |
| Zip | VARCHAR(10) | False |  | None |
| BillActive | TINYINT(1) | False | 0 | None |
| BillAddress1 | VARCHAR(40) | False |  | None |
| BillAddress2 | VARCHAR(40) | False |  | None |
| BillCity | VARCHAR(25) | False |  | None |
| BillName | VARCHAR(50) | False |  | None |
| BillState | CHAR(2) | False |  | None |
| BillZip | VARCHAR(10) | False |  | None |
| CommercialAccount | TINYINT(1) | True | None | None |
| DeliveryDirections | LONGTEXT | False | None | None |
| EmploymentStatus | ENUM(Unknown, Full Time, Part Time, Retired, Student, Unemployed) | False | Unknown | `EmploymentStatus` ENUM('Unknown', 'Full Time', 'Part Time', 'Retired', 'Student', 'Unemployed') NOT NULL DEFAULT 'Unknown' |
| Gender | ENUM(Male, Female) | False | Male | `Gender` ENUM('Male', 'Female') NOT NULL DEFAULT 'Male' |
| Height | DOUBLE | True | None | None |
| License | VARCHAR(50) | False |  | None |
| MaritalStatus | ENUM(Unknown, Single, Married, Legaly Separated, Divorced, Widowed) | False | Unknown | `MaritalStatus` ENUM('Unknown', 'Single', 'Married', 'Legaly Separated', 'Divorced', 'Widowed') NOT NULL DEFAULT 'Unknown' |
| MilitaryBranch | ENUM(N/A, Army, Air Force, Navy, Marines, Coast Guard, National Guard) | False | N/A | `MilitaryBranch` ENUM('N/A', 'Army', 'Air Force', 'Navy', 'Marines', 'Coast Guard', 'National Guard') NOT NULL DEFAULT 'N/A' |
| MilitaryStatus | ENUM(N/A, Active, Reserve, Retired) | False | N/A | `MilitaryStatus` ENUM('N/A', 'Active', 'Reserve', 'Retired') NOT NULL DEFAULT 'N/A' |
| ShipActive | TINYINT(1) | False | 0 | None |
| ShipAddress1 | VARCHAR(40) | False |  | None |
| ShipAddress2 | VARCHAR(40) | False |  | None |
| ShipCity | VARCHAR(25) | False |  | None |
| ShipName | VARCHAR(50) | False |  | None |
| ShipState | CHAR(2) | False |  | None |
| ShipZip | VARCHAR(10) | False |  | None |
| SSNumber | VARCHAR(50) | False |  | None |
| StudentStatus | ENUM(N/A, Full Time, Part Time) | False | N/A | `StudentStatus` ENUM('N/A', 'Full Time', 'Part Time') NOT NULL DEFAULT 'N/A' |
| Weight | DOUBLE | True | None | None |
| Basis | ENUM(Bill, Allowed) | False | Bill | `Basis` ENUM('Bill', 'Allowed') NOT NULL DEFAULT 'Bill' |
| Block12HCFA | TINYINT(1) | False | 0 | None |
| Block13HCFA | TINYINT(1) | False | 0 | None |
| CommercialAcctCreditLimit | DOUBLE | True | None | None |
| CommercialAcctTerms | VARCHAR(50) | False |  | None |
| CopayDollar | DOUBLE | True | None | None |
| Deductible | DOUBLE | True | None | None |
| Frequency | ENUM(Per Visit, Monthly, Yearly) | False | Per | `Frequency` ENUM('Per Visit', 'Monthly', 'Yearly') NOT NULL DEFAULT 'Per Visit' |
| Hardship | TINYINT(1) | False | 0 | None |
| MonthsValid | INT(11) | False | 0 | None |
| OutOfPocket | DOUBLE | True | None | None |
| SignatureOnFile | DATE | True | None | None |
| SignatureType | CHAR(1) | True | None | None |
| TaxRateID | INT(11) | True | None | None |
| Doctor1_ID | INT(11) | True | None | None |
| Doctor2_ID | INT(11) | True | None | None |
| EmergencyContact | LONGTEXT | False | None | None |
| FacilityID | INT(11) | True | None | None |
| LegalRepID | INT(11) | True | None | None |
| ReferralID | INT(11) | True | None | None |
| SalesRepID | INT(11) | True | None | None |
| AccidentType | ENUM(Auto, No, Other) | False | None | `AccidentType` ENUM('Auto', 'No', 'Other') NOT NULL |
| StateOfAccident | CHAR(2) | False |  | None |
| DateOfInjury | DATE | True | None | None |
| Emergency | TINYINT(1) | False | 0 | None |
| EmploymentRelated | TINYINT(1) | False | 0 | None |
| FirstConsultDate | DATE | True | None | None |
| ICD9_1 | VARCHAR(6) | True | None | None |
| ICD9_2 | VARCHAR(6) | True | None | None |
| ICD9_3 | VARCHAR(6) | True | None | None |
| ICD9_4 | VARCHAR(6) | True | None | None |
| POSTypeID | INT(11) | True | None | None |
| ReturnToWorkDate | DATE | True | None | None |
| CopayPercent | DOUBLE | True | None | None |
| SetupDate | DATE | False | 0000-00-00 | None |
| HIPPANote | TINYINT(1) | False | 0 | None |
| SupplierStandards | TINYINT(1) | False | 0 | None |
| InactiveDate | DATE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| InvoiceFormID | INT(11) | True | 4 | None |
| Email | VARCHAR(150) | True | None | None |
| Collections | BIT(1) | False | b'0 | None |
| ICD10_01 | VARCHAR(8) | True | None | None |
| ICD10_02 | VARCHAR(8) | True | None | None |
| ICD10_03 | VARCHAR(8) | True | None | None |
| ICD10_04 | VARCHAR(8) | True | None | None |
| ICD10_05 | VARCHAR(8) | True | None | None |
| ICD10_06 | VARCHAR(8) | True | None | None |
| ICD10_07 | VARCHAR(8) | True | None | None |
| ICD10_08 | VARCHAR(8) | True | None | None |
| ICD10_09 | VARCHAR(8) | True | None | None |
| ICD10_10 | VARCHAR(8) | True | None | None |
| ICD10_11 | VARCHAR(8) | True | None | None |
| ICD10_12 | VARCHAR(8) | True | None | None |

## Primary Key
- ID

## Engine
- InnoDB
