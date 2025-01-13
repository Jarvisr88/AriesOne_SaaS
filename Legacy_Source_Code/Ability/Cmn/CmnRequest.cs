namespace DMEWorks.Ability.Cmn
{
    using DMEWorks.Ability.Common;
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Schema;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true), XmlRoot("cmnRequest", Namespace="", IsNullable=false)]
    public class CmnRequest
    {
        [XmlElement("medicareMainframe", Form=XmlSchemaForm.Unqualified)]
        public DMEWorks.Ability.Common.MedicareMainframe MedicareMainframe { get; set; }

        [XmlElement("searchCriteria", Form=XmlSchemaForm.Unqualified)]
        public CmnRequestSearchCriteria SearchCriteria { get; set; }

        [XmlAttribute("mockResponse")]
        public bool MockResponse { get; set; }

        [XmlIgnore]
        public bool MockResponseSpecified { get; set; }
    }
}

