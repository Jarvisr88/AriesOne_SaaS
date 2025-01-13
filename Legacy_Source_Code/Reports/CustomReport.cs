namespace DMEWorks.Reports
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Serialization;

    public class CustomReport
    {
        [XmlAttribute]
        public string FileName { get; set; }

        [XmlIgnore]
        public bool IsDeleted { get; set; }

        [XmlAttribute]
        public byte Deleted
        {
            get => 
                !this.IsDeleted ? 0 : 1;
            set => 
                this.IsDeleted = value != 0;
        }

        [XmlAttribute]
        public string Category { get; set; }

        [XmlText]
        public string Name { get; set; }

        public bool DeletedSpecified =>
            this.IsDeleted;

        public bool CategorySpecified =>
            !this.IsDeleted;

        public bool NameSpecified =>
            !this.IsDeleted;
    }
}

