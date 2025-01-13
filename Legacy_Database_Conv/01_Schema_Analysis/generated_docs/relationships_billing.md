```mermaid
erDiagram
    %% BILLING Domain
    tbl_invoice {
        PK INT(11) ID
        FK INT(11) CustomerID
        FK INT(11) OrderID
        DATE InvoiceDate
        DATE SubmittedDate
        INT(11) POSTypeID
        SMALLINT(6) LastUpdateUserID
        TIMESTAMP LastUpdateDatetime
    }
```