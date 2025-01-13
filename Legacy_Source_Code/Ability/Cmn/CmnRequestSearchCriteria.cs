namespace DMEWorks.Ability.Cmn
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Schema;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true)]
    public class CmnRequestSearchCriteria
    {
        [XmlElement("npi", Form=XmlSchemaForm.Unqualified)]
        public string Npi { get; set; }

        [XmlElement("hic", Form=XmlSchemaForm.Unqualified)]
        public string Hic { get; set; }

        [XmlElement("hcpcs", Form=XmlSchemaForm.Unqualified)]
        public string Hcpcs { get; set; }

        [XmlElement("mbi", Form=XmlSchemaForm.Unqualified)]
        public string Mbi { get; set; }

        [XmlIgnore]
        public bool MbiSpecified { get; set; }

        [XmlAttribute("maxResults")]
        public int MaxResults { get; set; }

        [XmlIgnore]
        public bool MaxResultsSpecified { get; set; }
    }
}

