```mermaid
erDiagram
    %% INVENTORY Domain
    tbl_inventory {
        PK INT(11) WarehouseID
        PK INT(11) InventoryItemID
        SMALLINT(6) LastUpdateUserID
        TIMESTAMP LastUpdateDatetime
    }
```