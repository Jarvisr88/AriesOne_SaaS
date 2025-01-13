# Table: tbl_cmnform_0602b

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1 | ENUM(Y, N, D) | False | D | `Answer1` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer2 | DATE | True | None | None |
| Answer3 | ENUM(Y, N, D) | False | D | `Answer3` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer4 | INT(11) | True | None | None |
| Answer5 | ENUM(1, 2, 3, 4, 5) | False | 1 | `Answer5` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '1' |
| Answer6 | ENUM(Y, N, D) | False | D | `Answer6` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer7 | ENUM(Y, N, D) | False | D | `Answer7` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer8_begun | DATE | True | None | None |
| Answer8_ended | DATE | True | None | None |
| Answer9 | DATE | True | None | None |
| Answer10 | ENUM(1, 2, 3) | False | 1 | `Answer10` ENUM('1', '2', '3') NOT NULL DEFAULT '1' |
| Answer11 | ENUM(Y, N, D) | False | D | `Answer11` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer12 | ENUM(2, 4) | False | 2 | `Answer12` ENUM('2', '4') NOT NULL DEFAULT '2' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
