# Table: tbl_cmnform_4842

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1a | INT(11) | True | None | None |
| Answer1b | INT(11) | True | None | None |
| Answer1c | DATE | True | None | None |
| Answer2 | ENUM(Y, N) | False | Y | `Answer2` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |
| Answer3 | ENUM(1, 2, 3) | False | 1 | `Answer3` ENUM('1', '2', '3') NOT NULL DEFAULT '1' |
| PhysicianAddress | VARCHAR(50) | False |  | None |
| PhysicianCity | VARCHAR(50) | False |  | None |
| PhysicianState | VARCHAR(50) | False |  | None |
| PhysicianZip | VARCHAR(50) | False |  | None |
| PhysicianName | VARCHAR(50) | False |  | None |
| Answer5 | ENUM(Y, N, D) | False | D | `Answer5` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer6 | VARCHAR(10) | True | None | None |
| Answer7a | INT(11) | True | None | None |
| Answer7b | INT(11) | True | None | None |
| Answer7c | DATE | True | None | None |
| Answer8 | ENUM(Y, N, D) | False | D | `Answer8` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer9 | ENUM(Y, N, D) | False | D | `Answer9` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer10 | ENUM(Y, N, D) | False | D | `Answer10` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
