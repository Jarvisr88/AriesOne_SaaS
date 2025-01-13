namespace DMEWorks.Ability.Common
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Schema;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true)]
    public class Credential
    {
        [XmlElement("userId", Form=XmlSchemaForm.Unqualified)]
        public string UserId { get; set; }

        [XmlElement("password", Form=XmlSchemaForm.Unqualified)]
        public string Password { get; set; }
    }
}

