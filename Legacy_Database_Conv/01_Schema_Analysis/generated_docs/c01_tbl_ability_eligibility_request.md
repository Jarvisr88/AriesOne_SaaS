# Table: tbl_ability_eligibility_request

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| CustomerID | INT(11) | False | None | None |
| CustomerInsuranceID | INT(11) | False | None | None |
| RequestTime | DATETIME | False | None | None |
| RequestText | MEDIUMTEXT | False | None | None |
| ResponseTime | DATETIME | True | None | None |
| ResponseText | MEDIUMTEXT | True | None | None |
| SubmissionTime | DATETIME | True | None | None |
| SubmissionText | MEDIUMTEXT | True | None | None |

## Primary Key
- ID

## Engine
- InnoDB
