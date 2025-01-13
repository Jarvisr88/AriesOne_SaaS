namespace SODA.Models
{
    using SODA.Utilities;
    using System;
    using System.Runtime.CompilerServices;
    using System.Runtime.Serialization;

    [DataContract]
    public class LocationColumn
    {
        [OnDeserialized]
        internal void OnDeserializedMethod(StreamingContext contex)
        {
            this.HumanAddress = string.IsNullOrEmpty(this.HumanAddressJsonString) ? null : new SODA.Models.HumanAddress(this.HumanAddressJsonString);
        }

        [OnSerializing]
        internal void OnSerializingMethod(StreamingContext context)
        {
            this.HumanAddressJsonString = this.HumanAddress.ToJsonString();
        }

        [DataMember(Name="needs_recoding")]
        public bool NeedsRecoding { get; set; }

        [DataMember(Name="longitude")]
        public string Longitude { get; set; }

        [DataMember(Name="latitude")]
        public string Latitude { get; set; }

        public SODA.Models.HumanAddress HumanAddress { get; set; }

        [DataMember(Name="human_address")]
        internal string HumanAddressJsonString { get; set; }
    }
}

