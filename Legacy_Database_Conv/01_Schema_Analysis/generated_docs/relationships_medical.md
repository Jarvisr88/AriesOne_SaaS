```mermaid
erDiagram
    %% MEDICAL Domain
    tbl_cmnform {
        PK INT(11) ID
        ENUM(DMERC 01.02A, DMERC 01.02B, DMERC 02.03A, DMERC 02.03B, DMERC 03.02, DMERC 04.03B, DMERC 04.03C, DMERC 06.02B, DMERC 07.02A, DMERC 07.02B, DMERC 08.02, DMERC 09.02, DMERC 10.02A, DMERC 10.02B, DMERC 484.2, DMERC DRORDER, DMERC URO, DME 04.04B, DME 04.04C, DME 06.03B, DME 07.03A, DME 09.03, DME 10.03, DME 484.03) CMNType
        DATE InitialDate
        DATE RevisedDate
        DATE RecertificationDate
        INT(11) POSTypeID
        VARCHAR(50) AnsweringName
        VARCHAR(50) Signature_Name
        DATE Signature_Date
        SMALLINT(6) LastUpdateUserID
        TIMESTAMP LastUpdateDatetime
    }
```