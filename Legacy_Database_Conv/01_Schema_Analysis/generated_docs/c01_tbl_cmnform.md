# Table: tbl_cmnform

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| CMNType | ENUM(DMERC 01.02A, DMERC 01.02B, DMERC 02.03A, DMERC 02.03B, DMERC 03.02, DMERC 04.03B, DMERC 04.03C, DMERC 06.02B, DMERC 07.02A, DMERC 07.02B, DMERC 08.02, DMERC 09.02, DMERC 10.02A, DMERC 10.02B, DMERC 484.2, DMERC DRORDER, DMERC URO, DME 04.04B, DME 04.04C, DME 06.03B, DME 07.03A, DME 09.03, DME 10.03, DME 484.03) | False | DME | `CMNType` ENUM('DMERC 01.02A', 'DMERC 01.02B', 'DMERC 02.03A', 'DMERC 02.03B', 'DMERC 03.02', 'DMERC 04.03B', 'DMERC 04.03C', 'DMERC 06.02B', 'DMERC 07.02A', 'DMERC 07.02B', 'DMERC 08.02', 'DMERC 09.02', 'DMERC 10.02A', 'DMERC 10.02B', 'DMERC 484.2', 'DMERC DRORDER', 'DMERC URO', 'DME 04.04B', 'DME 04.04C', 'DME 06.03B', 'DME 07.03A', 'DME 09.03', 'DME 10.03', 'DME 484.03') NOT NULL DEFAULT 'DME 484.03' |
| InitialDate | DATE | True | None | None |
| RevisedDate | DATE | True | None | None |
| RecertificationDate | DATE | True | None | None |
| CustomerID | INT(11) | True | None | None |
| Customer_ICD9_1 | VARCHAR(8) | True | None | None |
| Customer_ICD9_2 | VARCHAR(8) | True | None | None |
| Customer_ICD9_3 | VARCHAR(8) | True | None | None |
| Customer_ICD9_4 | VARCHAR(8) | True | None | None |
| DoctorID | INT(11) | True | None | None |
| POSTypeID | INT(11) | True | None | None |
| FacilityID | INT(11) | True | None | None |
| AnsweringName | VARCHAR(50) | False |  | None |
| AnsweringTitle | VARCHAR(50) | False |  | None |
| AnsweringEmployer | VARCHAR(50) | False |  | None |
| EstimatedLengthOfNeed | INT(11) | False | 0 | None |
| Signature_Name | VARCHAR(50) | False |  | None |
| Signature_Date | DATE | True | None | None |
| OnFile | TINYINT(1) | False | 0 | None |
| OrderID | INT(11) | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| Customer_UsingICD10 | TINYINT(1) | False | 0 | None |

## Primary Key
- ID

## Engine
- InnoDB
