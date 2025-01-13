namespace DMEWorks.Ability.Common
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Schema;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true)]
    public class ErrorDetail
    {
        [XmlAttribute("value", Form=XmlSchemaForm.Unqualified)]
        public string Value { get; set; }

        [XmlAttribute("key", Form=XmlSchemaForm.Unqualified)]
        public string Key { get; set; }
    }
}

