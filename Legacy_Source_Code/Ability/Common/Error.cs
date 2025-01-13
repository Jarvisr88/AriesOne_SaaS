namespace DMEWorks.Ability.Common
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Schema;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true), XmlRoot("error", Namespace="", IsNullable=false)]
    public class Error
    {
        [XmlElement("code", Form=XmlSchemaForm.Unqualified)]
        public string Code { get; set; }

        [XmlElement("message", Form=XmlSchemaForm.Unqualified)]
        public string Message { get; set; }

        [XmlArray("details", Form=XmlSchemaForm.Unqualified), XmlArrayItem("detail", Form=XmlSchemaForm.Unqualified, IsNullable=false)]
        public ErrorDetail[] Details { get; set; }
    }
}

