# Table: tbl_cmnform_1002a

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| CMNFormID | INT(11) | False | 0 | None |
| Answer1 | ENUM(Y, N) | False | Y | `Answer1` ENUM('Y', 'N') NOT NULL DEFAULT 'Y' |
| Answer3 | INT(11) | True | None | None |
| Concentration_AminoAcid | DOUBLE | True | None | None |
| Concentration_Dextrose | DOUBLE | True | None | None |
| Concentration_Lipids | DOUBLE | True | None | None |
| Dose_AminoAcid | DOUBLE | True | None | None |
| Dose_Dextrose | DOUBLE | True | None | None |
| Dose_Lipids | DOUBLE | True | None | None |
| DaysPerWeek_Lipids | DOUBLE | True | None | None |
| GmsPerDay_AminoAcid | DOUBLE | True | None | None |
| Answer5 | ENUM(1, 3, 7) | False | 1 | `Answer5` ENUM('1', '3', '7') NOT NULL DEFAULT '1' |

## Primary Key
- CMNFormID

## Engine
- InnoDB
