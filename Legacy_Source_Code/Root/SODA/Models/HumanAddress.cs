namespace SODA.Models
{
    using Newtonsoft.Json;
    using System;
    using System.Runtime.CompilerServices;
    using System.Runtime.Serialization;

    [DataContract]
    public class HumanAddress : IEquatable<HumanAddress>
    {
        public HumanAddress()
        {
        }

        public HumanAddress(string humanAddressJson)
        {
            HumanAddress address = null;
            try
            {
                address = JsonConvert.DeserializeObject<HumanAddress>(humanAddressJson);
            }
            catch
            {
                throw new ArgumentOutOfRangeException("humanAddressJson", "The provided data was not parsable to a HumanAddress object.");
            }
            if ((address != null) && ((address.Address == null) && ((address.City == null) && ((address.State == null) && (address.Zip == null)))))
            {
                throw new ArgumentOutOfRangeException("humanAddressJson", "The provided data was not parsable to a HumanAddress object.");
            }
            this.Address = address.Address;
            this.City = address.City;
            this.State = address.State;
            this.Zip = address.Zip;
        }

        public bool Equals(HumanAddress other) => 
            (other != null) ? (this.Address.Equals(other.Address) && (this.City.Equals(other.City) && (this.State.Equals(other.State) && this.Zip.Equals(other.Zip)))) : false;

        [DataMember(Name="address")]
        public string Address { get; set; }

        [DataMember(Name="city")]
        public string City { get; set; }

        [DataMember(Name="state")]
        public string State { get; set; }

        [DataMember(Name="zip")]
        public string Zip { get; set; }
    }
}

