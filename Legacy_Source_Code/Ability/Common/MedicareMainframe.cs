namespace DMEWorks.Ability.Common
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Schema;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true)]
    public class MedicareMainframe
    {
        [XmlElement("application", Form=XmlSchemaForm.Unqualified)]
        public DMEWorks.Ability.Common.Application Application { get; set; }

        [XmlIgnore]
        public bool ApplicationSpecified { get; set; }

        [XmlElement("credential", Form=XmlSchemaForm.Unqualified)]
        public DMEWorks.Ability.Common.Credential Credential { get; set; }

        [XmlIgnore]
        public bool CredentialSpecified { get; set; }

        [XmlElement("clerkCredential", Form=XmlSchemaForm.Unqualified)]
        public DMEWorks.Ability.Common.Credential ClerkCredential { get; set; }

        [XmlIgnore]
        public bool ClerkCredentialSpecified { get; set; }
    }
}

