namespace DMEWorks.Ability.Common
{
    using System;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true)]
    public enum LineOfBusiness
    {
        PartA,
        HHH,
        PartB,
        DME,
        RuralHealth,
        FQHC,
        Section1011,
        Mutual,
        IndianHealth
    }
}

