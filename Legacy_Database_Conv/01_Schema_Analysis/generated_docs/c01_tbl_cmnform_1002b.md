# Table: tbl_cmnform_1002b

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer7 | ENUM(Y, N) | False | Y | `Answer7` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |
| Answer8 | ENUM(Y, N) | False | Y | `Answer8` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |
| Answer10a | VARCHAR(50) | False |  | None |
| Answer10b | VARCHAR(50) | False |  | None |
| Answer11a | VARCHAR(50) | False |  | None |
| Answer11b | VARCHAR(50) | False |  | None |
| Answer12 | INT(11) | True | None | None |
| Answer13 | ENUM(1, 2, 3, 4) | False | 1 | `Answer13` ENUM('1', '2', '3', '4') NOT NULL DEFAULT '1' |
| Answer14 | ENUM(Y, N, D) | False | D | `Answer14` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer15 | VARCHAR(50) | False |  | None |

## Primary Key
- CMNFormID

## Engine
- InnoDB
