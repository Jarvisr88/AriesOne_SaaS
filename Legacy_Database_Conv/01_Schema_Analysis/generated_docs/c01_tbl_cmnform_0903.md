# Table: tbl_cmnform_0903

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1a | VARCHAR(10) | True | None | None |
| Answer1b | VARCHAR(10) | True | None | None |
| Answer1c | VARCHAR(10) | True | None | None |
| Answer2a | VARCHAR(50) | True | None | None |
| Answer2b | VARCHAR(50) | True | None | None |
| Answer2c | VARCHAR(50) | True | None | None |
| Answer3 | ENUM(1, 2, 3, 4) | False | 1 | `Answer3` ENUM('1', '2', '3', '4') NOT NULL DEFAULT '1' |
| Answer4 | ENUM(1, 2) | False | 1 | `Answer4` ENUM('1', '2') NOT NULL DEFAULT '1' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
