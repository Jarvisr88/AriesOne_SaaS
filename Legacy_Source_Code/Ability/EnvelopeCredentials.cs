namespace DMEWorks.Ability
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true)]
    public class EnvelopeCredentials
    {
        [XmlElement("sender-id")]
        public string SenderId { get; set; }

        [XmlElement("username")]
        public string Username { get; set; }

        [XmlElement("password")]
        public string Password { get; set; }
    }
}

