# Table: tbl_cmnform_48403

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1a | INT(11) | True | None | None |
| Answer1b | INT(11) | True | None | None |
| Answer1c | DATE | True | None | None |
| Answer2 | ENUM(1, 2, 3) | False | 1 | `Answer2` ENUM('1', '2', '3') NOT NULL DEFAULT '1' |
| Answer3 | ENUM(1, 2, 3) | False | 1 | `Answer3` ENUM('1', '2', '3') NOT NULL DEFAULT '1' |
| Answer4 | ENUM(Y, N, D) | False | D | `Answer4` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer5 | VARCHAR(10) | True | None | None |
| Answer6a | INT(11) | True | None | None |
| Answer6b | INT(11) | True | None | None |
| Answer6c | DATE | True | None | None |
| Answer7 | ENUM(Y, N) | False | Y | `Answer7` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |
| Answer8 | ENUM(Y, N) | False | Y | `Answer8` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |
| Answer9 | ENUM(Y, N) | False | Y | `Answer9` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
