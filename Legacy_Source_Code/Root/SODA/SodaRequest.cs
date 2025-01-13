namespace SODA
{
    using Newtonsoft.Json;
    using System;
    using System.IO;
    using System.Net;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;
    using System.Text;
    using System.Xml;
    using System.Xml.Serialization;

    internal class SodaRequest
    {
        internal SodaRequest(Uri uri, string method, string appToken, string username, string password, SodaDataFormat dataFormat = 0, string payload = null, int? timeout = new int?())
        {
            this.dataFormat = dataFormat;
            HttpWebRequest request = WebRequest.Create(uri) as HttpWebRequest;
            request.Method = method.ToUpper();
            request.ProtocolVersion = new Version("1.1");
            request.PreAuthenticate = true;
            request.Timeout = (timeout != null) ? timeout.Value : request.Timeout;
            if (!string.IsNullOrEmpty(appToken))
            {
                request.Headers.Add("X-App-Token", appToken);
            }
            if (!string.IsNullOrEmpty(username) && !string.IsNullOrEmpty(password))
            {
                string s = $"{username}:{password}";
                byte[] bytes = Encoding.UTF8.GetBytes(s);
                request.Headers.Add("Authorization", $"Basic {Convert.ToBase64String(bytes)}");
            }
            switch (dataFormat)
            {
                case SodaDataFormat.JSON:
                    request.Accept = "application/json";
                    if (!request.Method.Equals("GET"))
                    {
                        request.ContentType = "application/json";
                    }
                    break;

                case SodaDataFormat.CSV:
                {
                    string str2 = request.Method;
                    if (str2 == "GET")
                    {
                        request.Accept = "text/csv";
                    }
                    else if ((str2 == "POST") || (str2 == "PUT"))
                    {
                        request.ContentType = "text/csv";
                    }
                    break;
                }
                case SodaDataFormat.XML:
                    request.Accept = "application/rdf+xml";
                    break;

                default:
                    break;
            }
            if (!string.IsNullOrEmpty(payload))
            {
                byte[] bytes = Encoding.UTF8.GetBytes(payload);
                using (Stream stream = request.GetRequestStream())
                {
                    stream.Write(bytes, 0, bytes.Length);
                }
            }
            this.webRequest = request;
        }

        internal TResult ParseResponse<TResult>() where TResult: class
        {
            TResult local = default(TResult);
            Exception innerException = null;
            bool flag = false;
            using (Stream stream = this.webRequest.GetResponse().GetResponseStream())
            {
                string str = new StreamReader(stream).ReadToEnd();
                switch (this.dataFormat)
                {
                    case SodaDataFormat.JSON:
                        try
                        {
                            local = JsonConvert.DeserializeObject<TResult>(str);
                        }
                        catch (JsonException exception1)
                        {
                            innerException = exception1;
                            flag = true;
                        }
                        break;

                    case SodaDataFormat.CSV:
                        local = str as TResult;
                        break;

                    case SodaDataFormat.XML:
                    {
                        Type type = typeof(TResult);
                        if (type == typeof(string))
                        {
                            local = str as TResult;
                        }
                        else
                        {
                            try
                            {
                                XmlReader xmlReader = XmlReader.Create(new StringReader(str));
                                local = new XmlSerializer(type).Deserialize(xmlReader) as TResult;
                            }
                            catch (Exception exception2)
                            {
                                innerException = exception2;
                                flag = true;
                            }
                        }
                        break;
                    }
                    default:
                        break;
                }
            }
            if (flag)
            {
                throw new InvalidOperationException($"Couldn't deserialize the ({this.dataFormat}) response into an instance of type {typeof(TResult)}.", innerException);
            }
            return local;
        }

        internal HttpWebRequest webRequest { get; private set; }

        internal SodaDataFormat dataFormat { get; private set; }
    }
}

