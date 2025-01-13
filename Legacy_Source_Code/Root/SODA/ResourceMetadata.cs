namespace SODA
{
    using Microsoft.CSharp.RuntimeBinder;
    using SODA.Utilities;
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Linq.Expressions;
    using System.Runtime.CompilerServices;
    using System.Runtime.Serialization;

    [DataContract]
    public class ResourceMetadata
    {
        internal ResourceMetadata()
        {
        }

        internal ResourceMetadata(SodaClient client)
        {
            if (client == null)
            {
                throw new ArgumentNullException("client", "Cannot initialize a ResourceMetadata with null SodaClient");
            }
            this.Client = client;
        }

        public SodaResult Update()
        {
            Uri uri = SodaUri.ForMetadata(this.Host, this.Identifier);
            SodaResult result = new SodaResult();
            try
            {
                result = this.Client.write<ResourceMetadata, SodaResult>(uri, "PUT", this);
                result.IsError = false;
                result.Message = $"Metadata for {this.Identifier} updated successfully.";
            }
            catch (Exception exception)
            {
                result.IsError = true;
                result.Message = exception.Message;
                result.Data = exception.StackTrace;
            }
            return result;
        }

        public SodaClient Client { get; internal set; }

        public string Host =>
            this.Client.Host;

        [DataMember(Name="id")]
        public string Identifier { get; internal set; }

        [DataMember(Name="name")]
        public string Name { get; set; }

        [DataMember(Name="category")]
        public string Category { get; set; }

        [DataMember(Name="description")]
        public string Description { get; set; }

        [DataMember(Name="tags")]
        public IEnumerable<string> Tags { get; set; }

        [DataMember(Name="attribution")]
        public string Attribution { get; set; }

        [DataMember(Name="attributionLink")]
        public string AttributionLink { get; set; }

        [DataMember(Name="createdAt")]
        public double? CreationDateUnix { get; internal set; }

        public DateTime? CreationDate
        {
            get
            {
                if (this.CreationDateUnix != null)
                {
                    return new DateTime?(DateTimeConverter.FromUnixTimestamp(this.CreationDateUnix.Value));
                }
                return null;
            }
        }

        [DataMember(Name="publicationDate")]
        public double? PublishedDateUnix { get; internal set; }

        public DateTime? PublishedDate
        {
            get
            {
                if (this.PublishedDateUnix != null)
                {
                    return new DateTime?(DateTimeConverter.FromUnixTimestamp(this.PublishedDateUnix.Value));
                }
                return null;
            }
        }

        [DataMember(Name="rowsUpdatedAt")]
        public double? RowsLastUpdatedUnix { get; internal set; }

        public DateTime? RowsLastUpdated
        {
            get
            {
                if (this.RowsLastUpdatedUnix != null)
                {
                    return new DateTime?(DateTimeConverter.FromUnixTimestamp(this.RowsLastUpdatedUnix.Value));
                }
                return null;
            }
        }

        [DataMember(Name="viewLastModified")]
        public double? SchemaLastUpdatedUnix { get; internal set; }

        public DateTime? SchemaLastUpdated
        {
            get
            {
                if (this.SchemaLastUpdatedUnix != null)
                {
                    return new DateTime?(DateTimeConverter.FromUnixTimestamp(this.SchemaLastUpdatedUnix.Value));
                }
                return null;
            }
        }

        [DataMember(Name="columns")]
        public IEnumerable<ResourceColumn> Columns { get; internal set; }

        [DataMember(Name="numberOfComments")]
        public long CommentsCount { get; private set; }

        [DataMember(Name="downloadCount")]
        public long DownloadsCount { get; private set; }

        [DataMember(Name="totalTimesRated")]
        public long RatingsCount { get; private set; }

        [DataMember(Name="averageRating")]
        public decimal AverageRating { get; private set; }

        [DataMember(Name="viewCount")]
        public long ViewsCount { get; private set; }

        [DataMember(Name="displayType")]
        public string DisplayType { get; private set; }

        [DataMember(Name="viewType")]
        public string ViewType { get; private set; }

        [DataMember(Name="tableId")]
        public long TableId { get; private set; }

        [Dynamic(new bool[] { false, false, true }), DataMember(Name="metadata")]
        [field: Dynamic(new bool[] { false, false, true })]
        public Dictionary<string, object> Metadata { [return: Dynamic(new bool[] { false, false, true })] get; [param: Dynamic(new bool[] { false, false, true })] set; }

        public long? RowIdentifierFieldId
        {
            get
            {
                if ((this.Metadata != null) && this.Metadata.ContainsKey("rowIdentifier"))
                {
                    long num;
                    if (<>o__99.<>p__2 == null)
                    {
                        CSharpArgumentInfo[] argumentInfo = new CSharpArgumentInfo[] { CSharpArgumentInfo.Create(CSharpArgumentInfoFlags.None, null) };
                        <>o__99.<>p__2 = CallSite<Func<CallSite, object, bool>>.Create(Binder.UnaryOperation(CSharpBinderFlags.None, ExpressionType.IsTrue, typeof(ResourceMetadata), argumentInfo));
                    }
                    if (<>o__99.<>p__1 == null)
                    {
                        CSharpArgumentInfo[] argumentInfo = new CSharpArgumentInfo[] { CSharpArgumentInfo.Create(CSharpArgumentInfoFlags.IsStaticType | CSharpArgumentInfoFlags.UseCompileTimeType, null), CSharpArgumentInfo.Create(CSharpArgumentInfoFlags.None, null), CSharpArgumentInfo.Create(CSharpArgumentInfoFlags.IsOut | CSharpArgumentInfoFlags.UseCompileTimeType, null) };
                        <>o__99.<>p__1 = CallSite<<>F{00000008}<CallSite, Type, object, long, object>>.Create(Binder.InvokeMember(CSharpBinderFlags.None, "TryParse", null, typeof(ResourceMetadata), argumentInfo));
                    }
                    if (<>o__99.<>p__0 == null)
                    {
                        CSharpArgumentInfo[] argumentInfo = new CSharpArgumentInfo[] { CSharpArgumentInfo.Create(CSharpArgumentInfoFlags.None, null) };
                        <>o__99.<>p__0 = CallSite<Func<CallSite, object, object>>.Create(Binder.InvokeMember(CSharpBinderFlags.None, "ToString", null, typeof(ResourceMetadata), argumentInfo));
                    }
                    if (<>o__99.<>p__2.Target(<>o__99.<>p__2, <>o__99.<>p__1.Target(<>o__99.<>p__1, typeof(long), <>o__99.<>p__0.Target(<>o__99.<>p__0, this.Metadata["rowIdentifier"]), ref num)))
                    {
                        return new long?(num);
                    }
                }
                return null;
            }
        }

        public string RowIdentifierField
        {
            get
            {
                if (this.RowIdentifierFieldId == null)
                {
                    if ((this.Metadata != null) && this.Metadata.ContainsKey("rowIdentifier"))
                    {
                        <>o__101.<>p__0 ??= CallSite<Func<CallSite, object, string>>.Create(Binder.Convert(CSharpBinderFlags.None, typeof(string), typeof(ResourceMetadata)));
                        return <>o__101.<>p__0.Target(<>o__101.<>p__0, this.Metadata["rowIdentifier"]);
                    }
                }
                else if ((this.Columns != null) && this.Columns.Any<ResourceColumn>())
                {
                    ResourceColumn column = this.Columns.SingleOrDefault<ResourceColumn>(c => c.Id.Equals(this.RowIdentifierFieldId.Value));
                    if (column != null)
                    {
                        return column.SodaFieldName;
                    }
                }
                return ":id";
            }
        }

        [Dynamic(new bool[] { false, false, true }), DataMember(Name="query")]
        [field: Dynamic(new bool[] { false, false, true })]
        public Dictionary<string, object> Query { [return: Dynamic(new bool[] { false, false, true })] get; [param: Dynamic(new bool[] { false, false, true })] set; }

        [Dynamic(new bool[] { false, false, true }), DataMember(Name="privateMetadata")]
        [field: Dynamic(new bool[] { false, false, true })]
        public Dictionary<string, object> PrivateMetadata { [return: Dynamic(new bool[] { false, false, true })] get; [param: Dynamic(new bool[] { false, false, true })] set; }

        public string ContactEmail
        {
            get
            {
                if ((this.PrivateMetadata == null) || !this.PrivateMetadata.ContainsKey("contactEmail"))
                {
                    return null;
                }
                <>o__111.<>p__0 ??= CallSite<Func<CallSite, object, string>>.Create(Binder.Convert(CSharpBinderFlags.ConvertExplicit, typeof(string), typeof(ResourceMetadata)));
                return <>o__111.<>p__0.Target(<>o__111.<>p__0, this.PrivateMetadata["contactEmail"]);
            }
        }

        [Dynamic(new bool[] { false, false, true }), DataMember(Name="viewFilters")]
        [field: Dynamic(new bool[] { false, false, true })]
        public Dictionary<string, object> ViewFilters { [return: Dynamic(new bool[] { false, false, true })] get; [param: Dynamic(new bool[] { false, false, true })] set; }

        [CompilerGenerated]
        private static class <>o__101
        {
            public static CallSite<Func<CallSite, object, string>> <>p__0;
        }

        [CompilerGenerated]
        private static class <>o__111
        {
            public static CallSite<Func<CallSite, object, string>> <>p__0;
        }

        [CompilerGenerated]
        private static class <>o__99
        {
            public static CallSite<Func<CallSite, object, object>> <>p__0;
            public static CallSite<<>F{00000008}<CallSite, Type, object, long, object>> <>p__1;
            public static CallSite<Func<CallSite, object, bool>> <>p__2;
        }
    }
}

