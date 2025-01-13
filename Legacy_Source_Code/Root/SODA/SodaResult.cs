namespace SODA
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Runtime.Serialization;

    [DataContract]
    public class SodaResult
    {
        [DataMember(Name="By RowIdentifier")]
        public int ByRowIdentifier { get; private set; }

        [DataMember(Name="Rows Updated")]
        public int RowsUpdated { get; private set; }

        [DataMember(Name="Rows Deleted")]
        public int RowsDeleted { get; private set; }

        [DataMember(Name="Rows Created")]
        public int RowsCreated { get; private set; }

        [DataMember(Name="Errors")]
        public int Errors { get; private set; }

        [DataMember(Name="By SID")]
        public int BySID { get; private set; }

        [DataMember(Name="message")]
        public string Message { get; internal set; }

        [DataMember(Name="error")]
        public bool IsError { get; internal set; }

        [DataMember(Name="code")]
        public string ErrorCode { get; internal set; }

        [Dynamic, DataMember(Name="data")]
        [field: Dynamic]
        public object Data { [return: Dynamic] get; [param: Dynamic] internal set; }
    }
}

