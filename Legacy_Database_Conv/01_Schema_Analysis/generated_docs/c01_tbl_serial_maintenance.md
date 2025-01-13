# Table: tbl_serial_maintenance

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| SerialID | INT(11) | False | None | None |
| AdditionalEquipment | TEXT | True | None | None |
| DescriptionOfProblem | TEXT | True | None | None |
| DescriptionOfWork | TEXT | True | None | None |
| MaintenanceRecord | TEXT | True | None | None |
| LaborHours | VARCHAR(255) | True | None | None |
| Technician | VARCHAR(255) | True | None | None |
| MaintenanceDue | DATE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
