namespace DMEWorks.Ability.Common
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Schema;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true)]
    public class Application
    {
        [XmlElement("facilityState", Form=XmlSchemaForm.Unqualified)]
        public string FacilityState { get; set; }

        [XmlIgnore]
        public bool FacilityStateSpecified { get; set; }

        [XmlElement("lineOfBusiness", Form=XmlSchemaForm.Unqualified)]
        public DMEWorks.Ability.Common.LineOfBusiness LineOfBusiness { get; set; }

        [XmlIgnore]
        public bool LineOfBusinessSpecified { get; set; }

        [XmlElement("name", Form=XmlSchemaForm.Unqualified)]
        public ApplicationName Name { get; set; }

        [XmlIgnore]
        public bool NameSpecified { get; set; }

        [XmlElement("dataCenter", Form=XmlSchemaForm.Unqualified)]
        public DataCenterType DataCenter { get; set; }

        [XmlIgnore]
        public bool DataCenterSpecified { get; set; }

        [XmlElement("appId", Form=XmlSchemaForm.Unqualified)]
        public string AppId { get; set; }

        [XmlIgnore]
        public bool AppIdSpecified { get; set; }

        [XmlElement("pptnRegion", Form=XmlSchemaForm.Unqualified)]
        public string PptnRegion { get; set; }

        [XmlIgnore]
        public bool PptnRegionSpecified { get; set; }
    }
}

