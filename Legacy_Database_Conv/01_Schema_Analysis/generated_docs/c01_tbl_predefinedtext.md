# Table: tbl_predefinedtext

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| Name | VARCHAR(50) | False |  | None |
| Type | ENUM(Document Text, Account Statements, Compliance Notes, Customer Notes, Invoice Notes, HAO) | False | Document | `Type` ENUM('Document Text', 'Account Statements', 'Compliance Notes', 'Customer Notes', 'Invoice Notes', 'HAO') NOT NULL DEFAULT 'Document Text' |
| Text | LONGTEXT | False | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

## Primary Key
- ID

## Engine
- InnoDB
