namespace DMEWorks.Csv
{
    using System;

    public enum ParseErrorAction
    {
        RaiseEvent,
        AdvanceToNextLine,
        ThrowException
    }
}

