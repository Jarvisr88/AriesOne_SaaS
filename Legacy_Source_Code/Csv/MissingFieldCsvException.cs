namespace DMEWorks.Csv
{
    using System;
    using System.Runtime.Serialization;

    [Serializable]
    public class MissingFieldCsvException : MalformedCsvException
    {
        public MissingFieldCsvException()
        {
        }

        public MissingFieldCsvException(string message) : base(message)
        {
        }

        protected MissingFieldCsvException(SerializationInfo info, StreamingContext context) : base(info, context)
        {
        }

        public MissingFieldCsvException(string message, Exception innerException) : base(message, innerException)
        {
        }

        public MissingFieldCsvException(string rawData, int currentPosition, long currentRecordIndex, int currentFieldIndex) : base(rawData, currentPosition, currentRecordIndex, currentFieldIndex)
        {
        }

        public MissingFieldCsvException(string rawData, int currentPosition, long currentRecordIndex, int currentFieldIndex, Exception innerException) : base(rawData, currentPosition, currentRecordIndex, currentFieldIndex, innerException)
        {
        }
    }
}

