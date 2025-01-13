namespace DMEWorks.Ability
{
    using System;
    using System.IO;
    using System.Runtime.CompilerServices;
    using System.Text;
    using System.Xml;
    using System.Xml.Serialization;

    [XmlType(AnonymousType=true), XmlRoot("settings", Namespace="", IsNullable=false)]
    public class IntegrationSettings
    {
        public static IntegrationSettings XmlDeserialize(string value)
        {
            using (StringReader reader = new StringReader(value ?? string.Empty))
            {
                return (IntegrationSettings) new XmlSerializer(typeof(IntegrationSettings)).Deserialize(reader);
            }
        }

        public static string XmlSerialize(IntegrationSettings settings)
        {
            if (settings == null)
            {
                return string.Empty;
            }
            XmlSerializerNamespaces namespaces = new XmlSerializerNamespaces();
            namespaces.Add(string.Empty, string.Empty);
            StringBuilder output = new StringBuilder();
            XmlWriterSettings settings1 = new XmlWriterSettings();
            settings1.Indent = true;
            settings1.OmitXmlDeclaration = true;
            using (XmlWriter writer = XmlWriter.Create(output, settings1))
            {
                new XmlSerializer(typeof(IntegrationSettings)).Serialize(writer, settings, namespaces);
            }
            return output.ToString();
        }

        [XmlElement("credentials")]
        public DMEWorks.Ability.Credentials Credentials { get; set; }

        [XmlElement("clerk-credentials")]
        public DMEWorks.Ability.Credentials ClerkCredentials { get; set; }

        [XmlElement("eligibility-credentials")]
        public AbilityCredentials EligibilityCredentials { get; set; }

        [XmlElement("envelope-credentials")]
        public DMEWorks.Ability.EnvelopeCredentials EnvelopeCredentials { get; set; }
    }
}

