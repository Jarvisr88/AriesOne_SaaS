namespace DMEWorks.Data.MySql
{
    using System;
    using System.Runtime.CompilerServices;

    public sealed class MySqlConnectionInfo
    {
        public MySqlConnectionInfo(MySqlServerInfo server, string username, string password, string database)
        {
            if (server == null)
            {
                MySqlServerInfo local1 = server;
                throw new ArgumentNullException("server");
            }
            this.<Server>k__BackingField = server;
            this.<Username>k__BackingField = username;
            this.<Password>k__BackingField = password;
            this.<Database>k__BackingField = database;
        }

        public string GetDatabaseConnectionString() => 
            this.Server.GetConnectionString(this.Username, this.Password, this.Database);

        public string GetDatabaseConnectionString(string initializationCommand) => 
            this.Server.GetConnectionString(this.Username, this.Password, this.Database, initializationCommand);

        public string GetServerConnectionString() => 
            this.Server.GetConnectionString(this.Username, this.Password, "mysql");

        public string GetServerConnectionString(string initializationCommand) => 
            this.Server.GetConnectionString(this.Username, this.Password, "mysql", initializationCommand);

        public MySqlServerInfo Server { get; }

        public string Username { get; }

        public string Password { get; }

        public string Database { get; }
    }
}

