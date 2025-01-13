namespace SODA
{
    using SODA.Utilities;
    using System;
    using System.Collections.Generic;

    public class Resource<TRow> where TRow: class
    {
        private readonly Lazy<ResourceMetadata> lazyMetadata;

        internal Resource(ResourceMetadata metadata)
        {
            this.lazyMetadata = new Lazy<ResourceMetadata>(() => metadata);
        }

        internal Resource(string resourceIdentifier, SodaClient client)
        {
            this.lazyMetadata = new Lazy<ResourceMetadata>(() => client.GetMetadata(resourceIdentifier));
        }

        public IEnumerable<SodaResult> BatchUpsert(IEnumerable<TRow> payload, int batchSize) => 
            this.Client.BatchUpsert<TRow>(payload, batchSize, this.Identifier);

        public IEnumerable<SodaResult> BatchUpsert(IEnumerable<TRow> payload, int batchSize, Func<IEnumerable<TRow>, TRow, bool> breakFunction) => 
            this.Client.BatchUpsert<TRow>(payload, batchSize, breakFunction, this.Identifier);

        public SodaResult DeleteRow(string rowId) => 
            this.Client.DeleteRow(rowId, this.Identifier);

        public TRow GetRow(string rowId)
        {
            if (string.IsNullOrEmpty(rowId))
            {
                throw new ArgumentException("rowId", "A row identifier is required.");
            }
            Uri uri = SodaUri.ForResourceAPI(this.Host, this.Identifier, rowId);
            return this.Client.read<TRow>(uri, SodaDataFormat.JSON);
        }

        public IEnumerable<TRow> GetRows() => 
            this.Query<TRow>(new SoqlQuery());

        public IEnumerable<TRow> GetRows(int limit)
        {
            SoqlQuery soqlQuery = new SoqlQuery().Limit(limit);
            return this.Query<TRow>(soqlQuery);
        }

        public IEnumerable<TRow> GetRows(int limit, int offset)
        {
            SoqlQuery soqlQuery = new SoqlQuery().Limit(limit).Offset(offset);
            return this.Query<TRow>(soqlQuery);
        }

        public IEnumerable<T> Query<T>(SoqlQuery soqlQuery) where T: class => 
            this.Client.Query<T>(soqlQuery, this.Identifier);

        public IEnumerable<TRow> Query(SoqlQuery soqlQuery) => 
            this.Query<TRow>(soqlQuery);

        public SodaResult Replace(IEnumerable<TRow> payload) => 
            this.Client.Replace<TRow>(payload, this.Identifier);

        public SodaResult Upsert(IEnumerable<TRow> payload) => 
            this.Client.Upsert<TRow>(payload, this.Identifier);

        public ResourceMetadata Metadata =>
            this.lazyMetadata.Value;

        public SodaClient Client =>
            this.Metadata.Client;

        public string Host =>
            this.Metadata.Host;

        public IEnumerable<ResourceColumn> Columns =>
            this.Metadata.Columns;

        public string Identifier =>
            this.Metadata.Identifier;
    }
}

