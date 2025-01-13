namespace Images.Service
{
    using Devart.Data.MySql;
    using DMEWorks.Core;
    using HtmlAgilityPack;
    using System;
    using System.Collections.Generic;
    using System.Collections.Specialized;
    using System.Data;
    using System.IO;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;
    using System.Text;
    using System.Text.RegularExpressions;
    using System.Xml;
    using System.Xml.Serialization;
    using System.Xml.XPath;

    public static class Templater
    {
        private const string CrLf = "\r\n";

        private static void ApplyFormData(HtmlNode node, string[] data)
        {
            string str2;
            if (node == null)
            {
                throw new ArgumentNullException("node");
            }
            if (node.Name == "button")
            {
                return;
            }
            if (node.Name != "input")
            {
                if (node.Name == "select")
                {
                    HashSet<string> set = null;
                    if (data != null)
                    {
                        set = new HashSet<string>(data, StringComparer.InvariantCultureIgnoreCase);
                    }
                    XPathNodeIterator iterator = node.CreateNavigator().Select("//option");
                    while (iterator.MoveNext())
                    {
                        string str3;
                        HtmlNode currentNode = ((HtmlNodeNavigator) iterator.Current).CurrentNode;
                        node.Attributes.Remove("selected");
                        if (node.Attributes.TryGetValue("value", out str3) && ((set != null) && set.Contains(str3)))
                        {
                            node.Attributes.Add("selected", "selected");
                        }
                    }
                    return;
                }
                if (node.Name == "textarea")
                {
                    node.RemoveAllChildren();
                    if (data != null)
                    {
                        node.AppendChild(node.OwnerDocument.CreateTextNode(string.Join("\r\n", data)));
                    }
                }
                return;
            }
            else
            {
                string str;
                if (!node.Attributes.TryGetValue("type", out str))
                {
                    return;
                }
                uint num = <PrivateImplementationDetails>.ComputeStringHash(str);
                if (num > 0xa38254c6)
                {
                    if (num > 0xccea6d90)
                    {
                        if (num > 0xd67a0605)
                        {
                            if (num == 0xf618f139)
                            {
                                bool flag5 = str == "hidden";
                                return;
                            }
                            if (num == 0xf7eb0225)
                            {
                                bool flag4 = str == "submit";
                                return;
                            }
                            if (num != 0xfadc0cd2)
                            {
                                return;
                            }
                            if (str != "range")
                            {
                                return;
                            }
                        }
                        else if (num == 0xd472dc59)
                        {
                            if (str != "date")
                            {
                                return;
                            }
                        }
                        else if (num == 0xd5c6965d)
                        {
                            if (str != "week")
                            {
                                return;
                            }
                        }
                        else
                        {
                            if (num != 0xd67a0605)
                            {
                                return;
                            }
                            if (str != "month")
                            {
                                return;
                            }
                        }
                    }
                    else if (num > 0xb35135fa)
                    {
                        if (num == 0xbde64e3e)
                        {
                            if (str != "text")
                            {
                                return;
                            }
                        }
                        else if (num == 0xbf01f77a)
                        {
                            if (str != "tel")
                            {
                                return;
                            }
                        }
                        else
                        {
                            if (num != 0xccea6d90)
                            {
                                return;
                            }
                            if (str != "datetime")
                            {
                                return;
                            }
                        }
                    }
                    else
                    {
                        if (num == 0xaaea5743)
                        {
                            bool flag2 = str == "file";
                            return;
                        }
                        if (num != 0xae401eb4)
                        {
                            if (num == 0xb35135fa)
                            {
                                bool flag6 = str == "image";
                            }
                            return;
                        }
                        if (str != "radio")
                        {
                            return;
                        }
                        goto TR_0013;
                    }
                    goto TR_0007;
                }
                else
                {
                    if (num > 0x3d7e6258)
                    {
                        if (num <= 0x650d33c0)
                        {
                            if (num == 0x43b27471)
                            {
                                bool flag1 = str == "button";
                                return;
                            }
                            if (num != 0x5d3c9be4)
                            {
                                if (num == 0x650d33c0)
                                {
                                    bool flag3 = str == "reset";
                                }
                                return;
                            }
                            if (str != "time")
                            {
                                return;
                            }
                        }
                        else if (num == 0x803328a9)
                        {
                            if (str != "search")
                            {
                                return;
                            }
                        }
                        else if (num == 0x8a8753c7)
                        {
                            if (str != "email")
                            {
                                return;
                            }
                        }
                        else
                        {
                            if (num != 0xa38254c6)
                            {
                                return;
                            }
                            if (str != "datetime-local")
                            {
                                return;
                            }
                        }
                    }
                    else if (num > 0x1bd670a0)
                    {
                        if (num == 0x328f4c1e)
                        {
                            if (str != "url")
                            {
                                return;
                            }
                        }
                        else
                        {
                            if (num == 0x364b5f18)
                            {
                                bool flag7 = str == "password";
                                return;
                            }
                            if (num != 0x3d7e6258)
                            {
                                return;
                            }
                            if (str != "color")
                            {
                                return;
                            }
                        }
                    }
                    else if (num == 0x6389b18)
                    {
                        if (str != "checkbox")
                        {
                            return;
                        }
                        goto TR_0013;
                    }
                    else
                    {
                        if (num != 0x1bd670a0)
                        {
                            return;
                        }
                        if (str != "number")
                        {
                            return;
                        }
                    }
                    goto TR_0007;
                }
            }
            goto TR_0013;
        TR_0007:
            node.Attributes.Remove("value");
            if (data != null)
            {
                node.Attributes.Add("value", string.Join("\r\n", data));
                return;
            }
            return;
        TR_0013:
            node.Attributes.Remove("checked");
            if ((data != null) && node.Attributes.TryGetValue("value", out str2))
            {
                for (int i = 0; i < data.Length; i++)
                {
                    if (string.Equals(str2, data[i], StringComparison.InvariantCultureIgnoreCase))
                    {
                        node.Attributes.Add("checked", "checked");
                        return;
                    }
                }
            }
        }

        private static NameValueCollection FetchBindingData(MySqlConnection connection, int? orderId)
        {
            NameValueCollection values;
            if (orderId == null)
            {
                values = new NameValueCollection();
                values.Add("tbl_customer.LastName", "Parker");
                values.Add("tbl_customer.FirstName", "Adam");
                values.Add("tbl_customer.Address1", "8882 Hillside Drive ");
                values.Add("tbl_customer.Address2", "");
                values.Add("tbl_customer.City", "Marlton");
                values.Add("tbl_customer.State", "NJ");
                values.Add("tbl_customer.Zip", "08053");
                values.Add("tbl_customer.Phone", "(856)219-8284");
                values.Add("tbl_order.ID", "######");
            }
            else
            {
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = "SELECT\r\n  tbl_customer.LastName  as `LastName`\r\n, tbl_customer.FirstName as `FirstName`\r\n, tbl_customer.Address1  as `Address1`\r\n, tbl_customer.Address2  as `Address2`\r\n, tbl_customer.City      as `City`\r\n, tbl_customer.State     as `State`\r\n, tbl_customer.Zip       as `Zip`\r\n, tbl_customer.Phone     as `Phone`\r\nFROM tbl_order\r\n     INNER JOIN tbl_customer ON tbl_customer.ID = tbl_order.CustomerID\r\nWHERE tbl_order.ID = :OrderID";
                    MySqlParameter parameter1 = new MySqlParameter("OrderID", MySqlType.Int);
                    parameter1.Value = orderId.Value;
                    command.Parameters.Add(parameter1);
                    using (MySqlDataReader reader = command.ExecuteReader(CommandBehavior.SingleRow | CommandBehavior.SingleResult))
                    {
                        if (!reader.Read())
                        {
                            throw new TemplateException("order does not exist");
                        }
                        values = new NameValueCollection();
                        int ordinal = 0;
                        int fieldCount = reader.FieldCount;
                        while (true)
                        {
                            if (ordinal >= fieldCount)
                            {
                                values.Add("tbl_order.ID", Convert.ToString(orderId.Value));
                                break;
                            }
                            values.Add("tbl_customer." + reader.GetName(ordinal), Convert.ToString(reader[ordinal]));
                            ordinal++;
                        }
                    }
                }
            }
            using (MySqlCommand command2 = connection.CreateCommand())
            {
                command2.CommandText = "SELECT\r\n  Name     as `Name`\r\n, Address1 as `Address1`\r\n, Address2 as `Address2`\r\n, City     as `City`\r\n, State    as `State`\r\n, Zip      as `Zip`\r\n, Phone    as `Phone`\r\nFROM tbl_company\r\nWHERE ID = 1";
                MySqlParameter parameter2 = new MySqlParameter("OrderID", MySqlType.Int);
                parameter2.Value = orderId;
                command2.Parameters.Add(parameter2);
                using (MySqlDataReader reader2 = command2.ExecuteReader(CommandBehavior.SingleRow | CommandBehavior.SingleResult))
                {
                    if (reader2.Read())
                    {
                        int ordinal = 0;
                        int fieldCount = reader2.FieldCount;
                        while (ordinal < fieldCount)
                        {
                            values.Add("tbl_company." + reader2.GetName(ordinal), Convert.ToString(reader2[ordinal]));
                            ordinal++;
                        }
                    }
                    else
                    {
                        return null;
                    }
                }
            }
            values["tbl_customer.Name"] = values["tbl_customer.LastName"] + ", " + values["tbl_customer.FirstName"];
            string[] textArray1 = new string[] { values["tbl_customer.City"], ", ", values["tbl_customer.State"], " ", values["tbl_customer.Zip"] };
            values["tbl_customer.CityStateZip"] = string.Concat(textArray1);
            string[] textArray2 = new string[] { values["tbl_company.City"], ", ", values["tbl_company.State"], " ", values["tbl_company.Zip"] };
            values["tbl_company.CityStateZip"] = string.Concat(textArray2);
            return values;
        }

        private static HtmlNode GetFormElement(HtmlDocument doc)
        {
            if (doc == null)
            {
                throw new ArgumentNullException("doc");
            }
            XPathNodeIterator iterator = doc.DocumentNode.CreateNavigator().Select("//form");
            if (!iterator.MoveNext())
            {
                throw new TemplateException("Document does not contain <form/> element");
            }
            HtmlNode currentNode = ((HtmlNodeNavigator) iterator.Current).CurrentNode;
            if (iterator.MoveNext())
            {
                throw new TemplateException("Document contains multiple <form/> elements");
            }
            return currentNode;
        }

        public static string GetPreview(string connectionString, string template)
        {
            NameValueCollection values;
            using (MySqlConnection connection = new MySqlConnection(connectionString))
            {
                connection.Open();
                int? orderId = null;
                values = FetchBindingData(connection, orderId);
            }
            using (StringWriter writer = new StringWriter())
            {
                Process(template, "Preview.aspx", null, values).Save(writer);
                return writer.ToString();
            }
        }

        public static string GetView(string connectionString, int orderId)
        {
            string str;
            string str2;
            NameValueCollection values;
            NameValueCollection values2;
            using (MySqlConnection connection = new MySqlConnection(connectionString))
            {
                connection.Open();
                values2 = FetchBindingData(connection, new int?(orderId));
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = "INSERT IGNORE INTO tbl_order_survey (SurveyID, OrderID, Form)\r\nSELECT tbl_survey.ID, tbl_order.ID, ''\r\nFROM tbl_order\r\n     INNER JOIN tbl_company ON tbl_company.ID = 1\r\n     INNER JOIN tbl_survey ON tbl_survey.ID = tbl_company.OrderSurveyID\r\nWHERE tbl_order.ID = :OrderID";
                    MySqlParameter parameter1 = new MySqlParameter("OrderID", MySqlType.Int);
                    parameter1.Value = orderId;
                    command.Parameters.Add(parameter1);
                    command.ExecuteNonQuery();
                }
                using (MySqlCommand command2 = connection.CreateCommand())
                {
                    command2.CommandText = "SELECT tbl_survey.Template, tbl_order_survey.Form\r\nFROM tbl_order_survey\r\n     INNER JOIN tbl_survey ON tbl_order_survey.SurveyID = tbl_survey.ID\r\nWHERE tbl_order_survey.OrderID = :OrderID";
                    MySqlParameter parameter2 = new MySqlParameter("OrderID", MySqlType.Int);
                    parameter2.Value = orderId;
                    command2.Parameters.Add(parameter2);
                    using (MySqlDataReader reader = command2.ExecuteReader(CommandBehavior.SingleRow | CommandBehavior.SingleResult))
                    {
                        if (!reader.Read())
                        {
                            throw new TemplateException("Survey for orders is not yet configured");
                        }
                        str = Convert.ToString(reader[0]);
                        values = XmlDeserialize(Convert.ToString(reader[1]));
                    }
                }
                str2 = "Survey.aspx?company=" + HttpUtility.UrlEncode(connection.Database) + "&orderid=" + orderId.ToString();
            }
            using (StringWriter writer = new StringWriter())
            {
                Process(str, str2, values, values2).Save(writer);
                return writer.ToString();
            }
        }

        private static HtmlDocument Process(string template, string action, NameValueCollection formData, NameValueCollection bindingData)
        {
            HtmlDocument doc = new HtmlDocument();
            doc.LoadHtml(template);
            HtmlNode formElement = GetFormElement(doc);
            formElement.Attributes.Remove("action");
            formElement.Attributes.Remove("method");
            formElement.Attributes.Remove("enctype");
            string text1 = action;
            if (action == null)
            {
                string local1 = action;
                text1 = string.Empty;
            }
            formElement.Attributes.Append("action", text1);
            HtmlNode local2 = formElement;
            local2.Attributes.Append("method", "post");
            XPathNavigator navigator = local2.CreateNavigator();
            if (navigator.SelectSingleNode("//input[@type='file']") != null)
            {
                throw new TemplateException("element <input type=\"file\" /> is not allowed");
            }
            if (navigator.SelectSingleNode("//input[@type='password']") != null)
            {
                throw new TemplateException("element <input type=\"password\" /> is not allowed");
            }
            Dictionary<string, List<HtmlNode>> dictionary = new Dictionary<string, List<HtmlNode>>(StringComparer.InvariantCultureIgnoreCase);
            XPathNodeIterator iterator = navigator.Select("(//button|//input|//select|//textarea)");
            while (iterator.MoveNext())
            {
                HtmlNode currentNode = ((HtmlNodeNavigator) iterator.Current).CurrentNode;
                currentNode.Attributes.Remove("formaction");
                currentNode.Attributes.Remove("formmethod");
                currentNode.Attributes.Remove("formenctype");
                currentNode.Attributes.Append("test", "test");
                HtmlAttribute attribute = currentNode.Attributes["name"];
                if (attribute != null)
                {
                    List<HtmlNode> list2;
                    if (!dictionary.TryGetValue(attribute.Value, out list2))
                    {
                        list2 = new List<HtmlNode>();
                        dictionary.Add(attribute.Value, list2);
                    }
                    list2.Add(currentNode);
                }
            }
            foreach (KeyValuePair<string, List<HtmlNode>> pair in dictionary)
            {
                string[] values = formData?.GetValues(pair.Key);
                using (List<HtmlNode>.Enumerator enumerator2 = pair.Value.GetEnumerator())
                {
                    while (enumerator2.MoveNext())
                    {
                        ApplyFormData(enumerator2.Current, values);
                    }
                }
            }
            List<HtmlCommentNode> list = new List<HtmlCommentNode>();
            XPathNodeIterator iterator2 = navigator.Select("//comment()");
            while (iterator2.MoveNext())
            {
                HtmlCommentNode currentNode = ((HtmlNodeNavigator) iterator2.Current).CurrentNode as HtmlCommentNode;
                if (currentNode != null)
                {
                    list.Add(currentNode);
                }
            }
            foreach (HtmlCommentNode node3 in list)
            {
                Match match = Regex.Match(node3.InnerText, @"<!--\s*dme-binding\s+(?<n>\S+)\s*-->", RegexOptions.ExplicitCapture | RegexOptions.IgnoreCase);
                if (match.Success)
                {
                    HtmlNode node4;
                    string str = match.Groups["n"].Value;
                    string text = bindingData?[str];
                    if (text != null)
                    {
                        node4 = doc.CreateTextNode(text);
                    }
                    else
                    {
                        node4 = doc.CreateElement("span");
                        node4.Attributes.Add("style", "background-color: yellow; border: 1px solid red;");
                        node4.InnerHtml = str;
                    }
                    node3.ParentNode.ReplaceChild(node4, node3);
                }
            }
            return doc;
        }

        public static bool SaveFormData(string connectionString, int orderId, NameValueCollection formData)
        {
            bool flag;
            using (MySqlConnection connection = new MySqlConnection(connectionString))
            {
                connection.Open();
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = "UPDATE tbl_order_survey\r\nSET Form = :Form\r\nWHERE tbl_order_survey.OrderID = :OrderID";
                    MySqlParameter parameter1 = new MySqlParameter("Form", MySqlType.Text, 0x10000);
                    parameter1.Value = XmlSerialize(formData);
                    command.Parameters.Add(parameter1);
                    MySqlParameter parameter2 = new MySqlParameter("OrderID", MySqlType.Int);
                    parameter2.Value = orderId;
                    command.Parameters.Add(parameter2);
                    flag = command.ExecuteNonQuery() == 1;
                }
            }
            return flag;
        }

        private static bool TryGetValue(this HtmlAttributeCollection collection, string name, out string value)
        {
            HtmlAttribute attribute = collection[name];
            if (attribute != null)
            {
                value = attribute.Value;
                return true;
            }
            value = string.Empty;
            return false;
        }

        public static void Validate(string template)
        {
            Process(template, "Preview.aspx", null, null);
        }

        public static NameValueCollection XmlDeserialize(string value)
        {
            List<NameValuePair> pairs;
            if (string.IsNullOrWhiteSpace(value))
            {
                return null;
            }
            try
            {
                using (StringReader reader = new StringReader(value))
                {
                    pairs = ((NameValuePairs) new XmlSerializer(typeof(NameValuePairs)).Deserialize(reader)).Pairs;
                }
            }
            catch (Exception)
            {
                return new NameValueCollection();
            }
            NameValueCollection values = new NameValueCollection();
            int num = 0;
            int count = pairs.Count;
            while (num < count)
            {
                NameValuePair pair = pairs[num];
                values.Add(pair.NameSpecified ? pair.Name : null, pair.ValueSpecified ? pair.Value : null);
                num++;
            }
            return values;
        }

        public static string XmlSerialize(NameValueCollection collection)
        {
            if (collection == null)
            {
                return string.Empty;
            }
            NameValuePairs o = new NameValuePairs();
            int index = 0;
            int count = collection.Count;
            while (index < count)
            {
                string key = collection.GetKey(index);
                string[] values = collection.GetValues(index);
                if ((values == null) || (values.Length == 0))
                {
                    o.Pairs.Add(new NameValuePair(key, null));
                }
                else
                {
                    for (int i = 0; i < values.Length; i++)
                    {
                        o.Pairs.Add(new NameValuePair(key, values[i]));
                    }
                }
                index++;
            }
            XmlSerializerNamespaces namespaces = new XmlSerializerNamespaces();
            namespaces.Add(string.Empty, string.Empty);
            StringBuilder output = new StringBuilder();
            XmlWriterSettings settings = new XmlWriterSettings();
            settings.Indent = true;
            settings.OmitXmlDeclaration = true;
            using (XmlWriter writer = XmlWriter.Create(output, settings))
            {
                new XmlSerializer(typeof(NameValuePairs)).Serialize(writer, o, namespaces);
            }
            return output.ToString();
        }

        public sealed class NameValuePair
        {
            public NameValuePair()
            {
            }

            public NameValuePair(string name, string value)
            {
                this.Name = name;
                this.Value = value;
                this.NameSpecified = name != null;
                this.ValueSpecified = value != null;
            }

            [XmlAttribute("name")]
            public string Name { get; set; }

            [XmlAttribute("value")]
            public string Value { get; set; }

            [XmlIgnore]
            public bool NameSpecified { get; set; }

            [XmlIgnore]
            public bool ValueSpecified { get; set; }
        }

        [XmlRoot("pairs")]
        public sealed class NameValuePairs
        {
            private List<Templater.NameValuePair> _pairs = new List<Templater.NameValuePair>();

            [XmlElement("pair")]
            public List<Templater.NameValuePair> Pairs =>
                this._pairs;
        }
    }
}

