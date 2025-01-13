```mermaid
erDiagram
    %% ORDER Domain
    tbl_order {
        PK INT(11) ID
        DATE OrderDate
        DATE DeliveryDate
        DATE BillDate
        DATE EndDate
        INT(11) POSTypeID
        SMALLINT(6) LastUpdateUserID
        TIMESTAMP LastUpdateDatetime
        ENUM(Retail, Back Office) SaleType
    }
```