namespace DMEWorks.Ability.Cmn
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Schema;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true), XmlRoot("cmnResponse", Namespace="", IsNullable=false)]
    public class CmnResponse
    {
        [XmlElement("numResults", Form=XmlSchemaForm.Unqualified)]
        public DateTime NumResults { get; set; }

        [XmlIgnore]
        public bool NumResultsSpecified { get; set; }

        [XmlElement("carrierNumber", Form=XmlSchemaForm.Unqualified)]
        public string CarrierNumber { get; set; }

        [XmlIgnore]
        public bool CarrierNumberSpecified { get; set; }

        [XmlElement("npi", Form=XmlSchemaForm.Unqualified)]
        public string Npi { get; set; }

        [XmlIgnore]
        public bool NpiSpecified { get; set; }

        [XmlElement("hic", Form=XmlSchemaForm.Unqualified)]
        public string Hicn { get; set; }

        [XmlIgnore]
        public bool HicnSpecified { get; set; }

        [XmlArray("certificatesOfMedicalNecessity", Form=XmlSchemaForm.Unqualified), XmlArrayItem("certificateOfMedicalNecessity", Form=XmlSchemaForm.Unqualified, IsNullable=false)]
        public CmnResponseEntry[] Claims { get; set; }
    }
}

