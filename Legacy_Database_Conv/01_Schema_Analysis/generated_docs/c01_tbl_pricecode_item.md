# Table: tbl_pricecode_item

**Database:** c01

## Columns

| Column | Data Type | Nullable | Default | Extra |
|--------|-----------|----------|---------|-------|
| AcceptAssignment | TINYINT(1) | False | 0 | None |
| OrderedQuantity | DOUBLE | False | 0 | None |
| OrderedUnits | VARCHAR(50) | True | None | None |
| OrderedWhen | ENUM(One time, Daily, Weekly, Monthly, Quarterly, Semi-Annually, Annually) | False | One | `OrderedWhen` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Semi-Annually', 'Annually') NOT NULL DEFAULT 'One time' |
| OrderedConverter | DOUBLE | False | 1 | None |
| BilledUnits | VARCHAR(50) | True | None | None |
| BilledWhen | ENUM(One time, Daily, Weekly, Monthly, Calendar Monthly, Quarterly, Semi-Annually, Annually, Custom) | False | One | `BilledWhen` ENUM('One time', 'Daily', 'Weekly', 'Monthly', 'Calendar Monthly', 'Quarterly', 'Semi-Annually', 'Annually', 'Custom') NOT NULL DEFAULT 'One time' |
| BilledConverter | DOUBLE | False | 1 | None |
| DeliveryUnits | VARCHAR(50) | True | None | None |
| DeliveryConverter | DOUBLE | False | 1 | None |
| BillingCode | VARCHAR(50) | True | None | None |
| BillItemOn | ENUM(Day of Delivery, Last day of the Month, Last day of the Period, Day of Pick-up) | False | Day | `BillItemOn` ENUM('Day of Delivery', 'Last day of the Month', 'Last day of the Period', 'Day of Pick-up') NOT NULL DEFAULT 'Day of Delivery' |
| DefaultCMNType | ENUM(DMERC 02.03A, DMERC 02.03B, DMERC 03.02, DMERC 07.02B, DMERC 08.02, DMERC DRORDER, DMERC URO, DME 04.04B, DME 04.04C, DME 06.03B, DME 07.03A, DME 09.03, DME 10.03, DME 484.03) | False | DME | `DefaultCMNType` ENUM('DMERC 02.03A', 'DMERC 02.03B', 'DMERC 03.02', 'DMERC 07.02B', 'DMERC 08.02', 'DMERC DRORDER', 'DMERC URO', 'DME 04.04B', 'DME 04.04C', 'DME 06.03B', 'DME 07.03A', 'DME 09.03', 'DME 10.03', 'DME 484.03') NOT NULL DEFAULT 'DME 484.03' |
| DefaultOrderType | ENUM(Sale, Rental) | False | Sale | `DefaultOrderType` ENUM('Sale', 'Rental') NOT NULL DEFAULT 'Sale' |
| AuthorizationTypeID | INT(11) | True | None | None |
| FlatRate | TINYINT(1) | False | 0 | None |
| ID | INT(11) | False | None | AUTO_INCREMENT |
| InventoryItemID | INT(11) | False | 0 | None |
| Modifier1 | VARCHAR(8) | False |  | None |
| Modifier2 | VARCHAR(8) | False |  | None |
| Modifier3 | VARCHAR(8) | False |  | None |
| Modifier4 | VARCHAR(8) | False |  | None |
| PriceCodeID | INT(11) | False | 0 | None |
| PredefinedTextID | INT(11) | True | None | None |
| RentalType | ENUM(Medicare Oxygen Rental, One Time Rental, Monthly Rental, Capped Rental, Parental Capped Rental, Rent to Purchase) | False | Monthly | `RentalType` ENUM('Medicare Oxygen Rental', 'One Time Rental', 'Monthly Rental', 'Capped Rental', 'Parental Capped Rental', 'Rent to Purchase') NOT NULL DEFAULT 'Monthly Rental' |
| ReoccuringSale | TINYINT(1) | False | 0 | None |
| ShowSpanDates | TINYINT(1) | False | 0 | None |
| Taxable | TINYINT(1) | False | 0 | None |
| LastUpdateUserID | SMALLINT(6) | True | None | None |
| LastUpdateDatetime | TIMESTAMP | False | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |
| BillInsurance | TINYINT(1) | False | 1 | None |
| DrugNoteField | VARCHAR(20) | True | None | None |
| DrugControlNumber | VARCHAR(50) | True | None | None |
| UserField1 | VARCHAR(100) | False |  | None |
| UserField2 | VARCHAR(100) | False |  | None |

## Primary Key
- ID

## Engine
- InnoDB
