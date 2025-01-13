namespace DMEWorks.Imaging
{
    using System;
    using System.Diagnostics;
    using System.IO;
    using System.Net;
    using System.Reflection;
    using System.Text;

    public class ImagingHelper
    {
        public const string ImagingStatus = "Imaging-Status";
        private readonly Uri uriget;
        private readonly Uri uriput;
        private readonly Uri uridel;

        public ImagingHelper(string server) : this(new Uri(server))
        {
        }

        public ImagingHelper(Uri server)
        {
            this.uridel = new Uri(server, "Del.aspx");
            this.uriget = new Uri(server, "Get.aspx");
            this.uriput = new Uri(server, "Put.aspx");
        }

        public void DelImage(string company, int imageIndex)
        {
            using (MemoryStream stream = new MemoryStream())
            {
                HttpHelper helper = new HttpHelper(stream);
                helper.AppendParameter("company", company);
                helper.AppendParameter("index", imageIndex.ToString());
                helper.CloseRequest();
                HttpWebRequest request = WebRequest.Create(this.uridel) as HttpWebRequest;
                request.Method = "POST";
                request.ContentType = "multipart/form-data; boundary=\"" + helper.boundary + "\"";
                request.ContentLength = stream.Length;
                using (Stream stream2 = request.GetRequestStream())
                {
                    stream.WriteTo(stream2);
                }
                using (WebResponse response = request.GetResponse())
                {
                    foreach (string str in response.Headers.Keys)
                    {
                        Trace.TraceInformation(str + ": " + response.Headers[str]);
                    }
                    if (string.Compare(response.Headers["Imaging-Status"], "Error", true) == 0)
                    {
                        using (StreamReader reader = new StreamReader(response.GetResponseStream()))
                        {
                            throw new Exception("Error executing request\r\n" + reader.ReadToEnd());
                        }
                    }
                }
            }
        }

        public byte[] GetImage(string company, int imageIndex)
        {
            byte[] buffer;
            HttpWebRequest request = WebRequest.Create(this.uriget) as HttpWebRequest;
            using (MemoryStream stream = new MemoryStream())
            {
                HttpHelper helper = new HttpHelper(stream);
                helper.AppendParameter("company", company);
                helper.AppendParameter("index", imageIndex.ToString());
                helper.CloseRequest();
                request.Method = "POST";
                request.ContentType = "multipart/form-data; boundary=\"" + helper.boundary + "\"";
                request.ContentLength = stream.Length;
                using (Stream stream2 = request.GetRequestStream())
                {
                    stream.WriteTo(stream2);
                }
            }
            using (WebResponse response = request.GetResponse())
            {
                foreach (string str in response.Headers.Keys)
                {
                    Trace.TraceInformation(str + ": " + response.Headers[str]);
                }
                if ("Error".Equals(response.Headers["Imaging-Status"], StringComparison.OrdinalIgnoreCase))
                {
                    using (StreamReader reader = new StreamReader(response.GetResponseStream()))
                    {
                        throw new Exception("Error executing request\r\n" + reader.ReadToEnd());
                    }
                }
                using (Stream stream3 = response.GetResponseStream())
                {
                    using (MemoryStream stream4 = new MemoryStream())
                    {
                        stream3.CopyTo(stream4);
                        stream4.Close();
                        buffer = stream4.ToArray();
                    }
                }
            }
            return buffer;
        }

        public void PutImage(string company, int imageIndex, byte[] data)
        {
            if (data == null)
            {
                throw new ArgumentNullException("data");
            }
            using (MemoryStream stream = new MemoryStream())
            {
                HttpHelper helper = new HttpHelper(stream);
                helper.AppendParameter("company", company);
                helper.AppendParameter("index", imageIndex.ToString());
                helper.AppendParameter("image", data);
                helper.CloseRequest();
                HttpWebRequest request = WebRequest.Create(this.uriput) as HttpWebRequest;
                request.Method = "POST";
                request.ContentType = "multipart/form-data; boundary=" + helper.boundary;
                request.ContentLength = stream.Length;
                using (Stream stream2 = request.GetRequestStream())
                {
                    stream.WriteTo(stream2);
                }
                using (HttpWebResponse response = (HttpWebResponse) request.GetResponse())
                {
                    foreach (string str in response.Headers.Keys)
                    {
                        Trace.TraceInformation(str + ": " + response.Headers[str]);
                    }
                    if (string.Compare(response.Headers["Imaging-Status"], "Error", true) == 0)
                    {
                        using (StreamReader reader = new StreamReader(response.GetResponseStream()))
                        {
                            throw new Exception("Error executing request\r\n" + reader.ReadToEnd());
                        }
                    }
                }
            }
        }

        private class HttpHelper : IDisposable
        {
            public readonly string boundary;
            public readonly Stream stream;
            public readonly StreamWriter writer;

            public HttpHelper(Stream stream)
            {
                if (stream == null)
                {
                    throw new ArgumentNullException("stream");
                }
                this.boundary = "---------------------" + DateTime.Now.Ticks.ToString("x");
                this.stream = stream;
                this.writer = new ClosableWriter(this.stream, Encoding.ASCII);
                this.writer.AutoFlush = true;
                this.writer.NewLine = "\r\n";
            }

            public void AppendParameter(string name, string value)
            {
                this.writer.WriteLine("--" + this.boundary);
                this.writer.WriteLine("Content-Disposition: form-data; name=\"" + name + "\"");
                this.writer.WriteLine();
                this.writer.WriteLine(value);
            }

            public void AppendParameter(string name, byte[] data)
            {
                this.writer.WriteLine("--" + this.boundary);
                this.writer.WriteLine("Content-Disposition: form-data; name=\"" + name + "\"");
                this.writer.WriteLine("Content-Type: application/octet-stream");
                this.writer.WriteLine("Content-Transfer-Encoding: binary");
                this.writer.WriteLine();
                this.stream.Write(data, 0, data.Length);
                this.writer.WriteLine();
            }

            public void CloseRequest()
            {
                this.writer.Write("--" + this.boundary + "--");
            }

            public void Dispose()
            {
                this.writer.Dispose();
            }

            private class ClosableWriter : StreamWriter
            {
                public ClosableWriter(Stream stream) : base(stream)
                {
                    this.SetClosable(false);
                }

                public ClosableWriter(Stream stream, Encoding encoding) : base(stream, encoding)
                {
                    this.SetClosable(false);
                }

                public ClosableWriter(Stream stream, Encoding encoding, int bufferSize) : base(stream, encoding, bufferSize)
                {
                    this.SetClosable(false);
                }

                private void SetClosable(bool value)
                {
                    Type type1 = typeof(StreamWriter);
                    type1.GetFields(BindingFlags.NonPublic | BindingFlags.Instance);
                    type1.GetField("closable", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(this, value);
                }
            }

            private class StreamWrapper : Stream
            {
                private readonly long origin;
                private Stream stream;

                public StreamWrapper(Stream stream)
                {
                    if (stream == null)
                    {
                        throw new ArgumentNullException("stream");
                    }
                    if (!stream.CanRead && !stream.CanWrite)
                    {
                        throw new ArgumentException("Stream is closed", "stream");
                    }
                    if (!stream.CanSeek)
                    {
                        throw new ArgumentException("Stream does not allow seek", "stream");
                    }
                    this.stream = stream;
                    this.origin = stream.Position;
                }

                protected override void Dispose(bool disposing)
                {
                    try
                    {
                        if (disposing && (this.stream != null))
                        {
                            this.stream.Flush();
                        }
                    }
                    finally
                    {
                        this.stream = null;
                        base.Dispose(disposing);
                    }
                }

                public override void Flush()
                {
                    if (this.stream == null)
                    {
                        StreamIsClosed();
                    }
                    this.stream.Flush();
                }

                public override int Read(byte[] array, int offset, int count)
                {
                    if (this.stream == null)
                    {
                        StreamIsClosed();
                    }
                    return this.stream.Read(array, offset, count);
                }

                public override int ReadByte()
                {
                    if (this.stream == null)
                    {
                        StreamIsClosed();
                    }
                    return this.stream.ReadByte();
                }

                public override long Seek(long offset, SeekOrigin origin)
                {
                    if (this.stream == null)
                    {
                        StreamIsClosed();
                    }
                    if (origin == SeekOrigin.Begin)
                    {
                        offset += this.origin;
                    }
                    return this.stream.Seek(offset, origin);
                }

                internal static void SeekNotSupported()
                {
                    throw new NotSupportedException("NotSupported_UnseekableStream");
                }

                public override void SetLength(long value)
                {
                    if (value < 0L)
                    {
                        throw new ArgumentOutOfRangeException("value", "Cannot be negative");
                    }
                    if (this.stream == null)
                    {
                        StreamIsClosed();
                    }
                    this.stream.SetLength(value);
                }

                internal static void StreamIsClosed()
                {
                    throw new ObjectDisposedException(null, "ObjectDisposed_StreamClosed");
                }

                public override void Write(byte[] array, int offset, int count)
                {
                    if (this.stream == null)
                    {
                        StreamIsClosed();
                    }
                    this.stream.Write(array, offset, count);
                }

                public override void WriteByte(byte value)
                {
                    if (this.stream == null)
                    {
                        StreamIsClosed();
                    }
                    this.stream.WriteByte(value);
                }

                public override bool CanRead =>
                    (this.stream != null) && this.stream.CanRead;

                public override bool CanSeek =>
                    (this.stream != null) && this.stream.CanSeek;

                public override bool CanWrite =>
                    (this.stream != null) && this.stream.CanWrite;

                public override long Length
                {
                    get
                    {
                        if (this.stream == null)
                        {
                            StreamIsClosed();
                        }
                        return (this.stream.Length - this.origin);
                    }
                }

                public override long Position
                {
                    get
                    {
                        if (this.stream == null)
                        {
                            StreamIsClosed();
                        }
                        return (this.stream.Position - this.origin);
                    }
                    set
                    {
                        if (this.stream == null)
                        {
                            StreamIsClosed();
                        }
                        this.stream.Position = this.origin + value;
                    }
                }
            }
        }
    }
}

