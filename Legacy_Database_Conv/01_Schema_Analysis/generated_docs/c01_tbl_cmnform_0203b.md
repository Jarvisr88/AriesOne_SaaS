# Table: tbl_cmnform_0203b

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1 | ENUM(Y, N, D) | False | D | `Answer1` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer2 | ENUM(Y, N, D) | False | D | `Answer2` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer3 | ENUM(Y, N, D) | False | D | `Answer3` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer4 | ENUM(Y, N, D) | False | D | `Answer4` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer5 | INT(11) | True | None | None |
| Answer8 | ENUM(Y, N, D) | False | D | `Answer8` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |
| Answer9 | ENUM(Y, N, D) | False | D | `Answer9` ENUM('Y', 'N', 'D') NOT NULL DEFAULT 'D' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
