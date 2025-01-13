# Table: tbl_cmnform_0102b

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer12 | ENUM(Y, N, D) | False | D | `Answer12` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer13 | ENUM(Y, N, D) | False | D | `Answer13` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer14 | ENUM(Y, N, D) | False | D | `Answer14` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer15 | ENUM(Y, N, D) | False | D | `Answer15` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer16 | ENUM(Y, N, D) | False | D | `Answer16` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer19 | ENUM(Y, N, D) | False | D | `Answer19` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer20 | ENUM(Y, N, D) | False | D | `Answer20` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer21_Ulcer1_Stage | VARCHAR(30) | True | None | None |
| Answer21_Ulcer1_MaxLength | DOUBLE | True | None | None |
| Answer21_Ulcer1_MaxWidth | DOUBLE | True | None | None |
| Answer21_Ulcer2_Stage | VARCHAR(30) | True | None | None |
| Answer21_Ulcer2_MaxLength | DOUBLE | True | None | None |
| Answer21_Ulcer2_MaxWidth | DOUBLE | True | None | None |
| Answer21_Ulcer3_Stage | VARCHAR(30) | True | None | None |
| Answer21_Ulcer3_MaxLength | DOUBLE | True | None | None |
| Answer21_Ulcer3_MaxWidth | DOUBLE | True | None | None |
| Answer22 | ENUM(1, 2, 3) | False | 1 | `Answer22` ENUM('1', '2', '3') NOT NULL DEFAULT '1' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
