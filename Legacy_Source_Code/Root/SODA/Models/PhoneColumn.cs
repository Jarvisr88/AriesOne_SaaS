namespace SODA.Models
{
    using Newtonsoft.Json;
    using System;
    using System.Runtime.CompilerServices;
    using System.Runtime.Serialization;

    [DataContract]
    public class PhoneColumn
    {
        public PhoneColumn()
        {
        }

        public PhoneColumn(string phoneJson)
        {
            PhoneColumn column = null;
            try
            {
                column = JsonConvert.DeserializeObject<PhoneColumn>(phoneJson);
            }
            catch
            {
                throw new ArgumentOutOfRangeException("phoneJson", "The provided data was not parsable to a PhoneColumn object.");
            }
            if ((column != null) && ((column.PhoneNumber == null) && (column.PhoneTypeString == null)))
            {
                throw new ArgumentOutOfRangeException("phoneJson", "The provided data was not parsable to a PhoneColumn object.");
            }
            this.PhoneNumber = column.PhoneNumber;
            this.PhoneType = column.PhoneType;
            this.PhoneTypeString = column.PhoneTypeString;
        }

        [OnDeserialized]
        internal void OnDeserializedMethod(StreamingContext contex)
        {
            PhoneColumnType type;
            if (Enum.TryParse<PhoneColumnType>(this.PhoneTypeString, out type))
            {
                this.PhoneType = type;
            }
            else
            {
                this.PhoneType = PhoneColumnType.Undefined;
            }
        }

        [OnSerializing]
        internal void OnSerializingMethod(StreamingContext context)
        {
            if (this.PhoneType == PhoneColumnType.Undefined)
            {
                this.PhoneTypeString = null;
            }
            else
            {
                this.PhoneTypeString = this.PhoneType.ToString();
            }
        }

        [DataMember(Name="phone_number")]
        public string PhoneNumber { get; set; }

        public PhoneColumnType PhoneType { get; set; }

        [DataMember(Name="phone_type")]
        internal string PhoneTypeString { get; set; }
    }
}

