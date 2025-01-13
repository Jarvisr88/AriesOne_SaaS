# Table: tbl_cmnform_1003

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1 | ENUM(Y, N) | False | Y | `Answer1` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |
| Answer2 | ENUM(Y, N) | False | Y | `Answer2` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |
| Answer3a | VARCHAR(10) | True | None | None |
| Answer3b | VARCHAR(10) | True | None | None |
| Answer4a | INT(11) | True | None | None |
| Answer4b | INT(11) | True | None | None |
| Answer5 | ENUM(1, 2, 3, 4) | False | 1 | `Answer5` ENUM('1', '2', '3', '4') NOT NULL DEFAULT '1' |
| Answer6 | INT(11) | True | None | None |
| Answer7 | ENUM(Y, N) | False | Y | `Answer7` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |
| Answer8a | INT(11) | True | None | None |
| Answer8b | INT(11) | True | None | None |
| Answer8c | INT(11) | True | None | None |
| Answer8d | INT(11) | True | None | None |
| Answer8e | INT(11) | True | None | None |
| Answer8f | INT(11) | True | None | None |
| Answer8g | INT(11) | True | None | None |
| Answer8h | INT(11) | True | None | None |
| Answer9 | ENUM(1, 2, 3) | False | 1 | `Answer9` ENUM('1', '2', '3') NOT NULL DEFAULT '1' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
