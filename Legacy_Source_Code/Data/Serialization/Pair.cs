namespace DMEWorks.Data.Serialization
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Serialization;

    public sealed class Pair
    {
        [XmlAttribute("n")]
        public string Name { get; set; }

        [XmlText]
        public string Value { get; set; }
    }
}

