namespace SODA
{
    using Microsoft.CSharp.RuntimeBinder;
    using Newtonsoft.Json;
    using SODA.Utilities;
    using System;
    using System.Collections;
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Linq;
    using System.Net;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;

    public class SodaClient
    {
        public readonly string Host;
        public readonly string AppToken;
        public readonly string Username;
        private readonly string password;

        public SodaClient(string host, string appToken = null) : this(host, appToken, null, null)
        {
        }

        public SodaClient(string host, string username, string password) : this(host, null, username, password)
        {
        }

        public SodaClient(string host, string appToken, string username, string password)
        {
            if (string.IsNullOrEmpty(host))
            {
                throw new ArgumentException("host", "A host is required");
            }
            this.Host = SodaUri.enforceHttps(host);
            this.AppToken = appToken;
            this.Username = username;
            this.password = password;
        }

        public IEnumerable<SodaResult> BatchUpsert<TRow>(IEnumerable<TRow> payload, int batchSize, string resourceId) where TRow: class
        {
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            if (string.IsNullOrEmpty(this.Username) || string.IsNullOrEmpty(this.password))
            {
                throw new InvalidOperationException("Write operations require an authenticated client.");
            }
            Func<IEnumerable<TRow>, TRow, bool> breakFunction = <>c__18<TRow>.<>9__18_0 ??= (a, b) => false;
            return this.BatchUpsert<TRow>(payload, batchSize, breakFunction, resourceId);
        }

        [IteratorStateMachine(typeof(<BatchUpsert>d__17))]
        public IEnumerable<SodaResult> BatchUpsert<TRow>(IEnumerable<TRow> payload, int batchSize, Func<IEnumerable<TRow>, TRow, bool> breakFunction, string resourceId) where TRow: class
        {
            <BatchUpsert>d__17<TRow> d__1 = new <BatchUpsert>d__17<TRow>(-2);
            d__1.<>4__this = this;
            d__1.<>3__payload = payload;
            d__1.<>3__batchSize = batchSize;
            d__1.<>3__breakFunction = breakFunction;
            d__1.<>3__resourceId = resourceId;
            return d__1;
        }

        public SodaResult DeleteRow(string rowId, string resourceId)
        {
            if (string.IsNullOrEmpty(rowId))
            {
                throw new ArgumentException("Must specify the row to be deleted using its row identifier.", "rowId");
            }
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            if (string.IsNullOrEmpty(this.Username) || string.IsNullOrEmpty(this.password))
            {
                throw new InvalidOperationException("Write operations require an authenticated client.");
            }
            int? timeout = null;
            return new SodaRequest(SodaUri.ForResourceAPI(this.Host, resourceId, rowId), "DELETE", this.AppToken, this.Username, this.password, SodaDataFormat.JSON, null, timeout).ParseResponse<SodaResult>();
        }

        public ResourceMetadata GetMetadata(string resourceId)
        {
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            Uri uri = SodaUri.ForMetadata(this.Host, resourceId);
            ResourceMetadata local1 = this.read<ResourceMetadata>(uri, SodaDataFormat.JSON);
            local1.Client = this;
            return local1;
        }

        [IteratorStateMachine(typeof(<GetMetadataPage>d__12))]
        public IEnumerable<ResourceMetadata> GetMetadataPage(int page)
        {
            <GetMetadataPage>d__12 d__1 = new <GetMetadataPage>d__12(-2);
            d__1.<>4__this = this;
            d__1.<>3__page = page;
            return d__1;
        }

        public Resource<TRow> GetResource<TRow>(string resourceId) where TRow: class
        {
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            return new Resource<TRow>(resourceId, this);
        }

        public IEnumerable<TRow> Query<TRow>(SoqlQuery soqlQuery, string resourceId) where TRow: class
        {
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            if ((soqlQuery.LimitValue > 0) || (soqlQuery.OffsetValue > 0))
            {
                Uri uri = SodaUri.ForQuery(this.Host, resourceId, soqlQuery);
                return this.read<IEnumerable<TRow>>(uri, SodaDataFormat.JSON);
            }
            List<TRow> list = new List<TRow>();
            int offset = 0;
            soqlQuery = soqlQuery.Limit(SoqlQuery.MaximumLimit).Offset(offset);
            for (IEnumerable<TRow> enumerable = this.read<IEnumerable<TRow>>(SodaUri.ForQuery(this.Host, resourceId, soqlQuery), SodaDataFormat.JSON); enumerable.Any<TRow>(); enumerable = this.read<IEnumerable<TRow>>(SodaUri.ForQuery(this.Host, resourceId, soqlQuery), SodaDataFormat.JSON))
            {
                list.AddRange(enumerable);
                soqlQuery = soqlQuery.Offset(++offset * SoqlQuery.MaximumLimit);
            }
            return list;
        }

        internal TResult read<TResult>(Uri uri, SodaDataFormat dataFormat = 0) where TResult: class => 
            new SodaRequest(uri, "GET", this.AppToken, this.Username, this.password, dataFormat, null, this.RequestTimeout).ParseResponse<TResult>();

        public SodaResult Replace<TRow>(IEnumerable<TRow> payload, string resourceId) where TRow: class
        {
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            if (string.IsNullOrEmpty(this.Username) || string.IsNullOrEmpty(this.password))
            {
                throw new InvalidOperationException("Write operations require an authenticated client.");
            }
            string str = JsonConvert.SerializeObject(payload);
            return this.Replace(str, SodaDataFormat.JSON, resourceId);
        }

        public SodaResult Replace(string payload, SodaDataFormat dataFormat, string resourceId)
        {
            if (dataFormat == SodaDataFormat.XML)
            {
                throw new ArgumentOutOfRangeException("dataFormat", "XML is not a valid format for write operations.");
            }
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            if (string.IsNullOrEmpty(this.Username) || string.IsNullOrEmpty(this.password))
            {
                throw new InvalidOperationException("Write operations require an authenticated client.");
            }
            int? timeout = null;
            SodaRequest request = new SodaRequest(SodaUri.ForResourceAPI(this.Host, resourceId, null), "PUT", this.AppToken, this.Username, this.password, dataFormat, payload, timeout);
            SodaResult result = null;
            try
            {
                if (dataFormat == SodaDataFormat.JSON)
                {
                    result = request.ParseResponse<SodaResult>();
                }
                else if (dataFormat == SodaDataFormat.CSV)
                {
                    result = JsonConvert.DeserializeObject<SodaResult>(request.ParseResponse<string>());
                }
            }
            catch (WebException exception)
            {
                string str = exception.UnwrapExceptionMessage();
                SodaResult result1 = new SodaResult();
                result1.Message = exception.Message;
                result1.IsError = true;
                result1.ErrorCode = str;
                result1.Data = payload;
                result = result1;
            }
            catch (Exception exception2)
            {
                SodaResult result2 = new SodaResult();
                result2.Message = exception2.Message;
                result2.IsError = true;
                result2.ErrorCode = exception2.Message;
                result2.Data = payload;
                result = result2;
            }
            return result;
        }

        public SodaResult Upsert<TRow>(IEnumerable<TRow> payload, string resourceId) where TRow: class
        {
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            if (string.IsNullOrEmpty(this.Username) || string.IsNullOrEmpty(this.password))
            {
                throw new InvalidOperationException("Write operations require an authenticated client.");
            }
            string str = JsonConvert.SerializeObject(payload);
            return this.Upsert(str, SodaDataFormat.JSON, resourceId);
        }

        public SodaResult Upsert(string payload, SodaDataFormat dataFormat, string resourceId)
        {
            if (dataFormat == SodaDataFormat.XML)
            {
                throw new ArgumentOutOfRangeException("dataFormat", "XML is not a valid format for write operations.");
            }
            if (FourByFour.IsNotValid(resourceId))
            {
                throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
            }
            if (string.IsNullOrEmpty(this.Username) || string.IsNullOrEmpty(this.password))
            {
                throw new InvalidOperationException("Write operations require an authenticated client.");
            }
            int? timeout = null;
            SodaRequest request = new SodaRequest(SodaUri.ForResourceAPI(this.Host, resourceId, null), "POST", this.AppToken, this.Username, this.password, dataFormat, payload, timeout);
            SodaResult result = null;
            try
            {
                if (dataFormat == SodaDataFormat.JSON)
                {
                    result = request.ParseResponse<SodaResult>();
                }
                else if (dataFormat == SodaDataFormat.CSV)
                {
                    result = JsonConvert.DeserializeObject<SodaResult>(request.ParseResponse<string>());
                }
            }
            catch (WebException exception)
            {
                string str = exception.UnwrapExceptionMessage();
                SodaResult result1 = new SodaResult();
                result1.Message = exception.Message;
                result1.IsError = true;
                result1.ErrorCode = str;
                result1.Data = payload;
                result = result1;
            }
            catch (Exception exception2)
            {
                SodaResult result2 = new SodaResult();
                result2.Message = exception2.Message;
                result2.IsError = true;
                result2.ErrorCode = exception2.Message;
                result2.Data = payload;
                result = result2;
            }
            return result;
        }

        internal TResult write<TPayload, TResult>(Uri uri, string method, TPayload payload) where TPayload: class where TResult: class => 
            new SodaRequest(uri, method, this.AppToken, this.Username, this.password, SodaDataFormat.JSON, payload.ToJsonString(), this.RequestTimeout).ParseResponse<TResult>();

        public int? RequestTimeout { get; set; }

        [Serializable, CompilerGenerated]
        private sealed class <>c__18<TRow> where TRow: class
        {
            public static readonly SodaClient.<>c__18<TRow> <>9;
            public static Func<IEnumerable<TRow>, TRow, bool> <>9__18_0;

            static <>c__18()
            {
                SodaClient.<>c__18<TRow>.<>9 = new SodaClient.<>c__18<TRow>();
            }

            internal bool <BatchUpsert>b__18_0(IEnumerable<TRow> a, TRow b) => 
                false;
        }

        [CompilerGenerated]
        private static class <>o__12
        {
            public static CallSite<Func<CallSite, object, object>> <>p__0;
            public static CallSite<Func<CallSite, object, string>> <>p__1;
        }

        [CompilerGenerated]
        private sealed class <BatchUpsert>d__17<TRow> : IEnumerable<SodaResult>, IEnumerable, IEnumerator<SodaResult>, IDisposable, IEnumerator where TRow: class
        {
            private int <>1__state;
            private SodaResult <>2__current;
            private int <>l__initialThreadId;
            private string resourceId;
            public string <>3__resourceId;
            public SodaClient <>4__this;
            private IEnumerable<TRow> payload;
            public IEnumerable<TRow> <>3__payload;
            private Func<IEnumerable<TRow>, TRow, bool> breakFunction;
            public Func<IEnumerable<TRow>, TRow, bool> <>3__breakFunction;
            private int batchSize;
            public int <>3__batchSize;
            private Queue<TRow> <queue>5__2;

            [DebuggerHidden]
            public <BatchUpsert>d__17(int <>1__state)
            {
                this.<>1__state = <>1__state;
                this.<>l__initialThreadId = Environment.CurrentManagedThreadId;
            }

            private bool MoveNext()
            {
                SodaResult result;
                int num = this.<>1__state;
                SodaClient client = this.<>4__this;
                if (num != 0)
                {
                    if (num != 1)
                    {
                        return false;
                    }
                    this.<>1__state = -1;
                }
                else
                {
                    this.<>1__state = -1;
                    if (FourByFour.IsNotValid(this.resourceId))
                    {
                        throw new ArgumentOutOfRangeException("resourceId", "The provided resourceId is not a valid Socrata (4x4) resource identifier.");
                    }
                    if (string.IsNullOrEmpty(client.Username) || string.IsNullOrEmpty(client.password))
                    {
                        throw new InvalidOperationException("Write operations require an authenticated client.");
                    }
                    this.<queue>5__2 = new Queue<TRow>(this.payload);
                }
                if (!this.<queue>5__2.Any<TRow>())
                {
                    return false;
                }
                List<TRow> list = new List<TRow>();
                for (int i = 0; ((i < this.batchSize) && (this.<queue>5__2.Count > 0)) && ((this.breakFunction == null) || !this.breakFunction(list, this.<queue>5__2.Peek())); i++)
                {
                    list.Add(this.<queue>5__2.Dequeue());
                }
                try
                {
                    result = client.Upsert<TRow>(list, this.resourceId);
                }
                catch (WebException exception)
                {
                    string str = exception.UnwrapExceptionMessage();
                    SodaResult result1 = new SodaResult();
                    result1.Message = exception.Message;
                    result1.IsError = true;
                    result1.ErrorCode = str;
                    result1.Data = this.payload;
                    result = result1;
                }
                catch (Exception exception2)
                {
                    SodaResult result2 = new SodaResult();
                    result2.Message = exception2.Message;
                    result2.IsError = true;
                    result2.ErrorCode = exception2.Message;
                    result2.Data = this.payload;
                    result = result2;
                }
                this.<>2__current = result;
                this.<>1__state = 1;
                return true;
            }

            [DebuggerHidden]
            IEnumerator<SodaResult> IEnumerable<SodaResult>.GetEnumerator()
            {
                SodaClient.<BatchUpsert>d__17<TRow> d__;
                if ((this.<>1__state == -2) && (this.<>l__initialThreadId == Environment.CurrentManagedThreadId))
                {
                    this.<>1__state = 0;
                    d__ = (SodaClient.<BatchUpsert>d__17<TRow>) this;
                }
                else
                {
                    d__ = new SodaClient.<BatchUpsert>d__17<TRow>(0) {
                        <>4__this = this.<>4__this
                    };
                }
                d__.payload = this.<>3__payload;
                d__.batchSize = this.<>3__batchSize;
                d__.breakFunction = this.<>3__breakFunction;
                d__.resourceId = this.<>3__resourceId;
                return d__;
            }

            [DebuggerHidden]
            IEnumerator IEnumerable.GetEnumerator() => 
                this.System.Collections.Generic.IEnumerable<SODA.SodaResult>.GetEnumerator();

            [DebuggerHidden]
            void IEnumerator.Reset()
            {
                throw new NotSupportedException();
            }

            [DebuggerHidden]
            void IDisposable.Dispose()
            {
            }

            SodaResult IEnumerator<SodaResult>.Current =>
                this.<>2__current;

            object IEnumerator.Current =>
                this.<>2__current;
        }

        [CompilerGenerated]
        private sealed class <GetMetadataPage>d__12 : IEnumerable<ResourceMetadata>, IEnumerable, IEnumerator<ResourceMetadata>, IDisposable, IEnumerator
        {
            private int <>1__state;
            private ResourceMetadata <>2__current;
            private int <>l__initialThreadId;
            private int page;
            public int <>3__page;
            public SodaClient <>4__this;
            private IEnumerator<object> <>7__wrap1;

            [DebuggerHidden]
            public <GetMetadataPage>d__12(int <>1__state)
            {
                this.<>1__state = <>1__state;
                this.<>l__initialThreadId = Environment.CurrentManagedThreadId;
            }

            private void <>m__Finally1()
            {
                this.<>1__state = -1;
                if (this.<>7__wrap1 != null)
                {
                    this.<>7__wrap1.Dispose();
                }
            }

            private bool MoveNext()
            {
                bool flag;
                try
                {
                    int num = this.<>1__state;
                    SodaClient client = this.<>4__this;
                    if (num == 0)
                    {
                        this.<>1__state = -1;
                        if (this.page <= 0)
                        {
                            throw new ArgumentOutOfRangeException("page", "Resouce metadata catalogs begin on page 1.");
                        }
                        IEnumerable<object> enumerable = client.read<IEnumerable<object>>(SodaUri.ForMetadataList(client.Host, this.page), SodaDataFormat.JSON).ToArray<object>();
                        this.<>7__wrap1 = enumerable.GetEnumerator();
                        this.<>1__state = -3;
                    }
                    else if (num == 1)
                    {
                        this.<>1__state = -3;
                    }
                    else
                    {
                        return false;
                    }
                    if (!this.<>7__wrap1.MoveNext())
                    {
                        this.<>m__Finally1();
                        this.<>7__wrap1 = null;
                        flag = false;
                    }
                    else
                    {
                        object current = this.<>7__wrap1.Current;
                        if (SodaClient.<>o__12.<>p__1 == null)
                        {
                            SodaClient.<>o__12.<>p__1 = CallSite<Func<CallSite, object, string>>.Create(Binder.Convert(CSharpBinderFlags.ConvertExplicit, typeof(string), typeof(SodaClient)));
                        }
                        if (SodaClient.<>o__12.<>p__0 == null)
                        {
                            CSharpArgumentInfo[] argumentInfo = new CSharpArgumentInfo[] { CSharpArgumentInfo.Create(CSharpArgumentInfoFlags.None, null) };
                            SodaClient.<>o__12.<>p__0 = CallSite<Func<CallSite, object, object>>.Create(Binder.GetMember(CSharpBinderFlags.None, "id", typeof(SodaClient), argumentInfo));
                        }
                        ResourceMetadata metadata = client.GetMetadata(SodaClient.<>o__12.<>p__1.Target(SodaClient.<>o__12.<>p__1, SodaClient.<>o__12.<>p__0.Target(SodaClient.<>o__12.<>p__0, current)));
                        this.<>2__current = metadata;
                        this.<>1__state = 1;
                        flag = true;
                    }
                }
                fault
                {
                    this.System.IDisposable.Dispose();
                }
                return flag;
            }

            [DebuggerHidden]
            IEnumerator<ResourceMetadata> IEnumerable<ResourceMetadata>.GetEnumerator()
            {
                SodaClient.<GetMetadataPage>d__12 d__;
                if ((this.<>1__state == -2) && (this.<>l__initialThreadId == Environment.CurrentManagedThreadId))
                {
                    this.<>1__state = 0;
                    d__ = this;
                }
                else
                {
                    d__ = new SodaClient.<GetMetadataPage>d__12(0) {
                        <>4__this = this.<>4__this
                    };
                }
                d__.page = this.<>3__page;
                return d__;
            }

            [DebuggerHidden]
            IEnumerator IEnumerable.GetEnumerator() => 
                this.System.Collections.Generic.IEnumerable<SODA.ResourceMetadata>.GetEnumerator();

            [DebuggerHidden]
            void IEnumerator.Reset()
            {
                throw new NotSupportedException();
            }

            [DebuggerHidden]
            void IDisposable.Dispose()
            {
                int num = this.<>1__state;
                if ((num == -3) || (num == 1))
                {
                    try
                    {
                    }
                    finally
                    {
                        this.<>m__Finally1();
                    }
                }
            }

            ResourceMetadata IEnumerator<ResourceMetadata>.Current =>
                this.<>2__current;

            object IEnumerator.Current =>
                this.<>2__current;
        }
    }
}

