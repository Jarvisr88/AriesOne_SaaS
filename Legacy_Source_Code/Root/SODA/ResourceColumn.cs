namespace SODA
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Runtime.Serialization;

    [DataContract]
    public class ResourceColumn
    {
        [DataMember(Name="id")]
        public long Id { get; internal set; }

        [DataMember(Name="name")]
        public string Name { get; set; }

        [DataMember(Name="dataTypeName")]
        public string DataTypeName { get; internal set; }

        [DataMember(Name="fieldName")]
        public string SodaFieldName { get; set; }

        [DataMember(Name="position")]
        public int Position { get; internal set; }

        [DataMember(Name="renderTypeName")]
        public string RenderType { get; internal set; }

        [DataMember(Name="tableColumnId")]
        public long TableColumnId { get; internal set; }
    }
}

