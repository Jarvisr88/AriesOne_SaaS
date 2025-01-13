namespace DMEWorks.Csv
{
    using System;

    public enum MissingFieldAction
    {
        TreatAsParseError,
        ReturnEmptyValue,
        ReturnNullValue,
        ReturnPartiallyParsedValue
    }
}

