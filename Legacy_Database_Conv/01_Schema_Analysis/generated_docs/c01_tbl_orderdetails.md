# Table: tbl_orderdetails

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| ID | INT(11) | False | None | AUTO_INCREMENT |
| OrderID | INT(11) | False | 0 | None |
| CustomerID | INT(11) | False | 0 | None |
| SerialNumber | VARCHAR(50) | True | None | None |
| InventoryItemID | INT(11) | False | 0 | None |
| PriceCodeID | INT(11) | False | 0 | None |
| SaleRentType | ENUM(Medicare Oxygen Rental, One Time Rental, Monthly Rental, Capped Rental, Parental Capped Rental, Rent to Purchase, One Time Sale, Re-occurring Sale) | False | Monthly | `SaleRentType` ENUM('Medicare Oxygen Rental', 'One Time Rental', 'Monthly Rental', 'Capped Rental', 'Parental Capped Rental', 'Rent to Purchase', 'One Time Sale', 'Re-occurring Sale') NOT NULL DEFAULT 'Monthly Rental' |
| SerialID | INT(11) | True | None | None |
| Taxable | TINYINT(1) | False | 0 | None |
| FlatRate | TINYINT(1) | False | 0 | None |
| DOSFrom | DATE | False | 0000-00-00 | None |
| DOSTo | DATE | True | None | None |
| PickupDate | DATE | True | None | None |
| ShowSpanDates | TINYINT(1) | False | 0 | None |
| OrderedQuantity | DOUBLE | False | 0 | None |
| OrderedUnits | VARCHAR(50) | True | None | None |
| OrderedWhen | ENUM(One time, Daily, Weekly, Monthly, Quarterly, Semi-Annually, Annually) | False | One | `OrderedWhen` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Semi-Annually', 'Annually') NOT NULL DEFAULT 'One time' |
| OrderedConverter | DOUBLE | False | 1 | None |
| BilledQuantity | DOUBLE | False | 0 | None |
| BilledUnits | VARCHAR(50) | True | None | None |
| BilledWhen | ENUM(One time, Daily, Weekly, Monthly, Calendar Monthly, Quarterly, Semi-Annually, Annually, Custom) | False | One | `BilledWhen` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Calendar Monthly', 'Quarterly', 'Semi-Annually', 'Annually', 'Custom') NOT NULL DEFAULT 'One time' |
| BilledConverter | DOUBLE | False | 1 | None |
| DeliveryQuantity | DOUBLE | False | 0 | None |
| DeliveryUnits | VARCHAR(50) | True | None | None |
| DeliveryConverter | DOUBLE | False | 1 | None |
| BillingCode | VARCHAR(50) | True | None | None |
| Modifier1 | VARCHAR(8) | False |  | None |
| Modifier2 | VARCHAR(8) | False |  | None |
| Modifier3 | VARCHAR(8) | False |  | None |
| Modifier4 | VARCHAR(8) | False |  | None |
| DXPointer | VARCHAR(50) | True | None | None |
| BillingMonth | INT(11) | False | 1 | None |
| BillItemOn | ENUM(Day of Delivery, Last day of the Month, Last day of the Period, Day of Pick-up) | False | Day | `BillItemOn` ENUM('Day of Delivery', 'Last day of the Month', 'Last day of the Period', 'Day of Pick-up') NOT NULL DEFAULT 'Day of Delivery' |
| AuthorizationNumber | VARCHAR(50) | True | None | None |
| AuthorizationTypeID | INT(11) | True | None | None |
| ReasonForPickup | VARCHAR(50) | True | None | None |
| SendCMN_RX_w_invoice | TINYINT(1) | False | 0 | None |
| MedicallyUnnecessary | TINYINT(1) | False | 0 | None |
| Sale | TINYINT(1) | False | 0 | None |
| SpecialCode | VARCHAR(50) | True | None | None |
| ReviewCode | VARCHAR(50) | True | None | None |
| NextOrderID | INT(11) | True | None | None |
| ReoccuringID | INT(11) | True | None | None |
| CMNFormID | INT(11) | True | None | None |
| HAOCode | VARCHAR(10) | True | None | None |
| State | ENUM(New, Approved, Pickup, Closed, Canceled) | False | New | `State` ENUM('New', 'Approved', 'Pickup', 'Closed', 'Canceled') NOT NULL DEFAULT 'New' |
| BillIns1 | TINYINT(1) | False | 1 | None |
| BillIns2 | TINYINT(1) | False | 1 | None |
| BillIns3 | TINYINT(1) | False | 1 | None |
| BillIns4 | TINYINT(1) | False | 1 | None |
| EndDate | DATE | True | None | None |
| NextBillingDate | DATE | True | None | None |
| WarehouseID | INT(11) | False | None | None |
| AcceptAssignment | TINYINT(1) | False | 0 | None |
| DrugNoteField | VARCHAR(20) | True | None | None |
| DrugControlNumber | VARCHAR(50) | True | None | None |
| NopayIns1 | TINYINT(1) | False | 0 | None |
| PointerICD10 | SMALLINT(6) | False | 0 | None |
| DXPointer10 | VARCHAR(50) | True | None | None |
| HaoDescription | VARCHAR(100) | True | None | None |
| UserField1 | VARCHAR(100) | False |  | None |
| UserField2 | VARCHAR(100) | False |  | None |
| AuthorizationExpirationDate | DATE | True | None | None |

## Primary Key
- ID

## Foreign Keys
- CustomerID, NextOrderID → c01.tbl_order (CustomerID, ID)
- CustomerID, OrderID → c01.tbl_order (CustomerID, ID)

## Engine
- InnoDB
