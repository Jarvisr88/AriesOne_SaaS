namespace DMEWorks.Csv
{
    using System;

    public class ParseErrorEventArgs : EventArgs
    {
        private MalformedCsvException _error;
        private ParseErrorAction _action;

        public ParseErrorEventArgs(MalformedCsvException error, ParseErrorAction defaultAction)
        {
            this._error = error;
            this._action = defaultAction;
        }

        public MalformedCsvException Error =>
            this._error;

        public ParseErrorAction Action
        {
            get => 
                this._action;
            set => 
                this._action = value;
        }
    }
}

