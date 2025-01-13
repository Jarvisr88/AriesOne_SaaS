namespace DMEWorks.Data
{
    using Devart.Data.MySql;
    using DMEWorks.Core;
    using System;

    public class Company
    {
        public readonly string Name;
        public readonly int? WarehouseID;
        public readonly int? POSTypeID;
        public readonly int? TaxRateID;
        public readonly int? OrderSurveyID;
        public readonly bool AutoGenerateAccountNumbers;
        public readonly bool AutoReorderInventory;
        public readonly bool ShowQuantityOnHand;
        public readonly Uri ImagingUri;

        public Company(Session session)
        {
            if (session == null)
            {
                throw new ArgumentNullException("session");
            }
            using (MySqlConnection connection = session.CreateConnection())
            {
                connection.Open();
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = "SELECT * FROM tbl_company WHERE ID = 1";
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        if (reader.Read())
                        {
                            this.Name = NullableConvert.ToString(reader["Name"]);
                            this.POSTypeID = NullableConvert.ToInt32(reader["POSTypeID"]);
                            this.WarehouseID = NullableConvert.ToInt32(reader["WarehouseID"]);
                            this.TaxRateID = NullableConvert.ToInt32(reader["TaxRateID"]);
                            this.OrderSurveyID = NullableConvert.ToInt32(reader["OrderSurveyID"]);
                            this.AutoGenerateAccountNumbers = NullableConvert.ToBoolean(reader["SystemGenerate_CustomerAccountNumbers"]).GetValueOrDefault(false);
                            this.AutoReorderInventory = NullableConvert.ToBoolean(reader["AutomaticallyReorderInventory"]).GetValueOrDefault(false);
                            this.ShowQuantityOnHand = NullableConvert.ToBoolean(reader["Show_QuantityOnHand"]).GetValueOrDefault(false);
                            this.ImagingUri = BuildImagingUri(NullableConvert.ToString(reader["ImagingServer"]), session.DsnInfo.Server.Server);
                        }
                    }
                }
            }
        }

        private static Uri BuildImagingUri(string url, string serverName)
        {
            Uri uri;
            if (!Uri.TryCreate(url, UriKind.Absolute, out uri))
            {
                return null;
            }
            if (!"dme-server-host".Equals(uri.Host, StringComparison.OrdinalIgnoreCase))
            {
                return uri;
            }
            UriBuilder builder1 = new UriBuilder(url);
            builder1.Host = serverName;
            return builder1.Uri;
        }
    }
}

