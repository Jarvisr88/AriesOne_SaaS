# Table: tbl_payer

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| InsuranceCompanyID | INT(11) | False | None | None |
| ParticipatingProvider | TINYINT(1) | False | 0 | None |
| LastUpdateUserID | SMALLINT(6) | False | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| ExtractOrderingPhysician | TINYINT(1) | False | 1 | None |
| ExtractReferringPhysician | TINYINT(1) | False | 0 | None |
| ExtractRenderingProvider | TINYINT(1) | False | 0 | None |
| TaxonomyCodePrefix | VARCHAR(10) | False |  | None |

## Primary Key
- InsuranceCompanyID

## Engine
- InnoDB
