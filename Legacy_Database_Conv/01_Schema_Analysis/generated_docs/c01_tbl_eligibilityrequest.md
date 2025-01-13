# Table: tbl_eligibilityrequest

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| CustomerID | INT(11) | False | 0 | None |
| CustomerInsuranceID | INT(11) | False | 0 | None |
| Region | ENUM(Region A, Region B, Region C, Region D, Zirmed, Medi-Cal, Availity, Office Ally, Ability) | False | Region | `Region` ENUM('Region A', 'Region B', 'Region C', 'Region D', 'Zirmed', 'Medi-Cal', 'Availity', 'Office Ally', 'Ability') NOT NULL DEFAULT 'Region A' |
| RequestBatchID | INT(11) | True | None | None |
| RequestTime | DATETIME | False | 1900-01-01 | 00:00:00' |
| RequestText | MEDIUMTEXT | False | None | None |
| ResponseBatchID | INT(11) | True | None | None |
| ResponseTime | DATETIME | True | None | None |
| ResponseText | MEDIUMTEXT | True | None | None |
| SubmissionTime | DATETIME | True | None | None |
| SubmissionText | MEDIUMTEXT | True | None | None |

## Primary Key
- ID

## Engine
- InnoDB
