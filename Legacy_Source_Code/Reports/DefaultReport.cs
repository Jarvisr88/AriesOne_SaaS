namespace DMEWorks.Reports
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Serialization;

    public class DefaultReport
    {
        [XmlAttribute]
        public string FileName { get; set; }

        [XmlIgnore]
        public bool IsSystem { get; set; }

        [XmlAttribute]
        public byte System
        {
            get => 
                !this.IsSystem ? 0 : 1;
            set => 
                this.IsSystem = value != 0;
        }

        public bool SystemSpecified =>
            this.IsSystem;

        [XmlText]
        public string Name { get; set; }

        [XmlAttribute]
        public string Category { get; set; }
    }
}

