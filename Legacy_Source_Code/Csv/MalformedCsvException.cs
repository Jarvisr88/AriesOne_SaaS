namespace DMEWorks.Csv
{
    using DMEWorks.Csv.Resources;
    using System;
    using System.Globalization;
    using System.Runtime.Serialization;

    [Serializable]
    public class MalformedCsvException : Exception
    {
        private string _message;
        private string _rawData;
        private int _currentFieldIndex;
        private long _currentRecordIndex;
        private int _currentPosition;

        public MalformedCsvException() : this((string) null, (Exception) null)
        {
        }

        public MalformedCsvException(string message) : this(message, null)
        {
        }

        protected MalformedCsvException(SerializationInfo info, StreamingContext context) : base(info, context)
        {
            this._message = info.GetString("MyMessage");
            this._rawData = info.GetString("RawData");
            this._currentPosition = info.GetInt32("CurrentPosition");
            this._currentRecordIndex = info.GetInt64("CurrentRecordIndex");
            this._currentFieldIndex = info.GetInt32("CurrentFieldIndex");
        }

        public MalformedCsvException(string message, Exception innerException) : base(string.Empty, innerException)
        {
            this._message = (message == null) ? string.Empty : message;
            this._rawData = string.Empty;
            this._currentPosition = -1;
            this._currentRecordIndex = -1L;
            this._currentFieldIndex = -1;
        }

        public MalformedCsvException(string rawData, int currentPosition, long currentRecordIndex, int currentFieldIndex) : this(rawData, currentPosition, currentRecordIndex, currentFieldIndex, null)
        {
        }

        public MalformedCsvException(string rawData, int currentPosition, long currentRecordIndex, int currentFieldIndex, Exception innerException) : base(string.Empty, innerException)
        {
            this._rawData = (rawData == null) ? string.Empty : rawData;
            this._currentPosition = currentPosition;
            this._currentRecordIndex = currentRecordIndex;
            this._currentFieldIndex = currentFieldIndex;
            object[] args = new object[] { this._currentRecordIndex, this._currentFieldIndex, this._currentPosition, this._rawData };
            this._message = string.Format(CultureInfo.InvariantCulture, ExceptionMessage.MalformedCsvException, args);
        }

        public override void GetObjectData(SerializationInfo info, StreamingContext context)
        {
            base.GetObjectData(info, context);
            info.AddValue("MyMessage", this._message);
            info.AddValue("RawData", this._rawData);
            info.AddValue("CurrentPosition", this._currentPosition);
            info.AddValue("CurrentRecordIndex", this._currentRecordIndex);
            info.AddValue("CurrentFieldIndex", this._currentFieldIndex);
        }

        public string RawData =>
            this._rawData;

        public int CurrentPosition =>
            this._currentPosition;

        public long CurrentRecordIndex =>
            this._currentRecordIndex;

        public int CurrentFieldIndex =>
            this._currentFieldIndex;

        public override string Message =>
            this._message;
    }
}

