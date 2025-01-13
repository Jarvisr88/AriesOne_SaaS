# Table: tbl_cmnform_0603b

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1 | ENUM(Y, N) | False | N | `Answer1` ENUM('Y', 'N') NOT NULL DEFAULT 'N' |
| Answer2 | INT(11) | True | None | None |
| Answer3 | ENUM(1, 2, 3, 4, 5) | False | 5 | `Answer3` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '5' |
| Answer4 | ENUM(Y, N) | False | N | `Answer4` ENUM('Y', 'N') NOT NULL DEFAULT 'N' |
| Answer5 | ENUM(Y, N) | False | N | `Answer5` ENUM('Y', 'N') NOT NULL DEFAULT 'N' |
| Answer6 | DATE | True | None | None |

## Primary Key
- CMNFormID

## Engine
- InnoDB
