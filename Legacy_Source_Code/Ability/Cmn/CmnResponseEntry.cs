namespace DMEWorks.Ability.Cmn
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Xml.Schema;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true)]
    public class CmnResponseEntry
    {
        [XmlElement("submittedHcpcs", Form=XmlSchemaForm.Unqualified)]
        public string SubmittedHcpcs { get; set; }

        [XmlIgnore]
        public bool SubmittedHcpcsSpecified { get; set; }

        [XmlElement("approvedHcpcs", Form=XmlSchemaForm.Unqualified)]
        public string ApprovedHcpcs { get; set; }

        [XmlIgnore]
        public bool ApprovedHcpcsSpecified { get; set; }

        [XmlElement("initialDate", Form=XmlSchemaForm.Unqualified)]
        public string InitialDate { get; set; }

        [XmlIgnore]
        public bool InitialDateSpecified { get; set; }

        [XmlElement("statusCode", Form=XmlSchemaForm.Unqualified)]
        public string StatusCode { get; set; }

        [XmlIgnore]
        public bool StatusCodeSpecified { get; set; }

        [XmlElement("statusDescription", Form=XmlSchemaForm.Unqualified)]
        public string StatusDescription { get; set; }

        [XmlIgnore]
        public bool StatusDescriptionSpecified { get; set; }

        [XmlElement("statusDate", Form=XmlSchemaForm.Unqualified)]
        public string StatusDate { get; set; }

        [XmlIgnore]
        public bool StatusDateSpecified { get; set; }

        [XmlElement("lengthOfNeed", Form=XmlSchemaForm.Unqualified)]
        public string LengthOfNeed { get; set; }

        [XmlIgnore]
        public bool LengthOfNeedSpecified { get; set; }

        [XmlElement("typeValue", Form=XmlSchemaForm.Unqualified)]
        public string TypeValue { get; set; }

        [XmlIgnore]
        public bool TypeValueSpecified { get; set; }

        [XmlElement("typeDescription", Form=XmlSchemaForm.Unqualified)]
        public string TypeDescription { get; set; }

        [XmlIgnore]
        public bool TypeDescriptionSpecified { get; set; }

        [XmlElement("totalRentalPayments", Form=XmlSchemaForm.Unqualified)]
        public string TotalRentalPayments { get; set; }

        [XmlIgnore]
        public bool TotalRentalPaymentsSpecified { get; set; }

        [XmlElement("recertificationRevisedDate", Form=XmlSchemaForm.Unqualified)]
        public string RecertificationRevisedDate { get; set; }

        [XmlIgnore]
        public bool RecertificationRevisedDateSpecified { get; set; }

        [XmlElement("lastClaimDate", Form=XmlSchemaForm.Unqualified)]
        public string LastClaimDate { get; set; }

        [XmlIgnore]
        public bool LastClaimDateSpecified { get; set; }

        [XmlElement("supplierName", Form=XmlSchemaForm.Unqualified)]
        public string SupplierName { get; set; }

        [XmlIgnore]
        public bool SupplierNameSpecified { get; set; }

        [XmlElement("supplierPhone", Form=XmlSchemaForm.Unqualified)]
        public string SupplierPhone { get; set; }

        [XmlIgnore]
        public bool SupplierPhoneSpecified { get; set; }
    }
}

