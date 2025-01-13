# Table: tbl_cmnform_0902

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1 | ENUM(1, 3, 4) | False | 1 | `Answer1` ENUM('1', '3', '4') NOT NULL DEFAULT '1' |
| Answer2 | VARCHAR(50) | False |  | None |
| Answer3 | VARCHAR(50) | False |  | None |
| Answer4 | ENUM(1, 3, 4) | False | 1 | `Answer4` ENUM('1', '3', '4') NOT NULL DEFAULT '1' |
| Answer5 | ENUM(1, 2, 3) | False | 1 | `Answer5` ENUM('1', '2', '3') NOT NULL DEFAULT '1' |
| Answer6 | INT(11) | False | 1 | None |
| Answer7 | ENUM(Y, N, D) | False | D | `Answer7` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
