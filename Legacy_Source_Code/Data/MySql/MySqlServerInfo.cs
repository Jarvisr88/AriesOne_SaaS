namespace DMEWorks.Data.MySql
{
    using Devart.Data.MySql;
    using System;
    using System.Configuration;
    using System.Runtime.CompilerServices;

    public sealed class MySqlServerInfo
    {
        public static readonly int? DefaultCommandTimeout;

        static MySqlServerInfo()
        {
            int num;
            if (int.TryParse(ConfigurationManager.AppSettings["MySql:DefaultCommandTimeout"], out num) && (15 < num))
            {
                DefaultCommandTimeout = new int?(num);
            }
        }

        public MySqlServerInfo(string server, int port) : this(server, port, false)
        {
        }

        public MySqlServerInfo(string server, int port, bool compress)
        {
            this.<Server>k__BackingField = server;
            this.<Port>k__BackingField = port;
            this.<Compress>k__BackingField = compress;
        }

        private MySqlConnectionStringBuilder CreateBuilder(string username, string password)
        {
            MySqlConnectionStringBuilder builder1 = new MySqlConnectionStringBuilder();
            builder1.Host = this.Server;
            builder1.Port = this.Port;
            builder1.Compress = this.Compress;
            builder1.UserId = username;
            builder1.Password = password;
            builder1.Charset = "latin1";
            builder1.FoundRows = true;
            MySqlConnectionStringBuilder builder = builder1;
            if (DefaultCommandTimeout != null)
            {
                builder.DefaultCommandTimeout = DefaultCommandTimeout.Value;
            }
            return builder;
        }

        public string GetConnectionString(string username, string password) => 
            this.CreateBuilder(username, password).ConnectionString;

        public string GetConnectionString(string username, string password, string database)
        {
            MySqlConnectionStringBuilder builder1 = this.CreateBuilder(username, password);
            builder1.Database = database;
            return builder1.ConnectionString;
        }

        public string GetConnectionString(string username, string password, string database, string initializationCommand)
        {
            MySqlConnectionStringBuilder builder1 = this.CreateBuilder(username, password);
            builder1.Database = database;
            builder1.InitializationCommand = initializationCommand;
            return builder1.ConnectionString;
        }

        public static bool IsSystemDatabase(string database) => 
            string.Equals(database, "mysql", StringComparison.OrdinalIgnoreCase) || (string.Equals(database, "sys", StringComparison.OrdinalIgnoreCase) || (string.Equals(database, "information_schema", StringComparison.OrdinalIgnoreCase) || string.Equals(database, "performance_schema", StringComparison.OrdinalIgnoreCase)));

        public string Server { get; }

        public int Port { get; }

        public bool Compress { get; }
    }
}

