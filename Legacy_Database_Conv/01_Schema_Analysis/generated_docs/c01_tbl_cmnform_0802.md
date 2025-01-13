# Table: tbl_cmnform_0802

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1_HCPCS | VARCHAR(5) | False |  | None |
| Answer1_MG | INT(11) | True | None | None |
| Answer1_Times | INT(11) | True | None | None |
| Answer2_HCPCS | VARCHAR(5) | False |  | None |
| Answer2_MG | INT(11) | True | None | None |
| Answer2_Times | INT(11) | True | None | None |
| Answer3_HCPCS | VARCHAR(5) | False |  | None |
| Answer3_MG | INT(11) | True | None | None |
| Answer3_Times | INT(11) | True | None | None |
| Answer4 | ENUM(Y, N) | False | N | `Answer4` ENUM('Y', 'N') NOT NULL DEFAULT 'N' |
| Answer5_1 | ENUM(1, 2, 3, 4, 5) | False | 1 | `Answer5_1` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '1' |
| Answer5_2 | ENUM(1, 2, 3, 4, 5) | False | 1 | `Answer5_2` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '1' |
| Answer5_3 | ENUM(1, 2, 3, 4, 5) | False | 1 | `Answer5_3` ENUM('1', '2', '3', '4', '5') NOT NULL DEFAULT '1' |
| Answer8 | VARCHAR(60) | False |  | None |
| Answer9 | VARCHAR(20) | False |  | None |
| Answer10 | VARCHAR(2) | False |  | None |
| Answer11 | DATE | True | None | None |
| Answer12 | ENUM(Y, N) | False | N | `Answer12` ENUM('Y', 'N') NOT NULL DEFAULT 'N' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
