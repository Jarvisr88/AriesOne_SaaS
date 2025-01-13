namespace DMEWorks.Data.Serialization
{
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Text;
    using System.Text.RegularExpressions;
    using System.Xml;
    using System.Xml.Serialization;

    [XmlRoot("values")]
    public sealed class Pairs
    {
        private List<Pair> _elements = new List<Pair>();

        public static Pairs PlainDeserialize(string value)
        {
            Pairs pairs = new Pairs();
            for (Match match = Regex.Match(value ?? string.Empty, "(?<name>[^=\r\n]+)=(?<value>[^\r\n]*)[\r\n]*", RegexOptions.Singleline | RegexOptions.ExplicitCapture | RegexOptions.IgnoreCase); match.Success; match = match.NextMatch())
            {
                Group group = match.Groups["name"];
                Group group2 = match.Groups["value"];
                Pair item = new Pair();
                item.Name = group.Value;
                item.Value = group2.Value;
                pairs.Elements.Add(item);
            }
            return pairs;
        }

        public static string PlainSerialize(Pairs pairs)
        {
            if ((pairs == null) || (pairs.Elements.Count == 0))
            {
                return string.Empty;
            }
            StringBuilder builder = new StringBuilder();
            foreach (Pair pair in pairs.Elements)
            {
                if (0 < builder.Length)
                {
                    builder.AppendLine();
                }
                builder.Append(pair.Name).Append('=').Append(pair.Value);
            }
            return builder.ToString();
        }

        public static Pairs XmlDeserialize(string value)
        {
            using (StringReader reader = new StringReader(value ?? string.Empty))
            {
                return (Pairs) new XmlSerializer(typeof(Pairs)).Deserialize(reader);
            }
        }

        public static string XmlSerialize(Pairs pairs)
        {
            if ((pairs == null) || (pairs.Elements.Count == 0))
            {
                return string.Empty;
            }
            XmlSerializerNamespaces namespaces = new XmlSerializerNamespaces();
            namespaces.Add(string.Empty, string.Empty);
            StringBuilder output = new StringBuilder();
            XmlWriterSettings settings = new XmlWriterSettings();
            settings.Indent = true;
            settings.OmitXmlDeclaration = true;
            using (XmlWriter writer = XmlWriter.Create(output, settings))
            {
                new XmlSerializer(typeof(Pairs)).Serialize(writer, pairs, namespaces);
            }
            return output.ToString();
        }

        [XmlElement("v")]
        public List<Pair> Elements =>
            this._elements;
    }
}

