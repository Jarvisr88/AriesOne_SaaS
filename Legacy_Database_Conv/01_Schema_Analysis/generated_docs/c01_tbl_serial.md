# Table: tbl_serial

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| CurrentCustomerID | INT(11) | True | None | None |
| InventoryItemID | INT(11) | False | 0 | None |
| LastCustomerID | INT(11) | True | None | None |
| ManufacturerID | INT(11) | True | None | None |
| VendorID | INT(11) | True | None | None |
| WarehouseID | INT(11) | True | None | None |
| LengthOfWarranty | VARCHAR(50) | False |  | None |
| LotNumber | VARCHAR(50) | False |  | None |
| MaintenanceRecord | LONGTEXT | False | None | None |
| ManufaturerSerialNumber | VARCHAR(50) | False |  | None |
| ModelNumber | VARCHAR(50) | False |  | None |
| MonthsRented | VARCHAR(50) | False |  | None |
| NextMaintenanceDate | DATE | True | None | None |
| PurchaseOrderID | INT(11) | True | None | None |
| PurchaseAmount | DOUBLE | False | 0 | None |
| PurchaseDate | DATE | True | None | None |
| SerialNumber | VARCHAR(50) | False |  | None |
| SoldDate | DATE | True | None | None |
| Status | ENUM(Empty, Filled, Junked, Lost, Reserved, On Hand, Rented, Sold, Sent, Maintenance, Transferred Out) | False | Empty | `Status` ENUM('Empty', 'Filled', 'Junked', 'Lost', 'Reserved', 'On Hand', 'Rented', 'Sold', 'Sent', 'Maintenance', 'Transferred Out') NOT NULL DEFAULT 'Empty' |
| Warranty | VARCHAR(50) | False |  | None |
| OwnRent | ENUM(Own, Rent) | False | Own | `OwnRent` ENUM('Own', 'Rent') NOT NULL DEFAULT 'Own' |
| FirstRented | DATE | True | None | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| ConsignmentType | VARCHAR(20) | True | None | None |
| ConsignmentName | VARCHAR(50) | True | None | None |
| ConsignmentDate | DATETIME | True | None | None |
| VendorStockNumber | VARCHAR(20) | True | None | None |
| LotNumberExpires | DATETIME | True | None | None |

## Primary Key
- ID

## Engine
- InnoDB
