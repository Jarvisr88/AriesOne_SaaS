namespace DMEWorks.Data
{
    using Devart.Data.MySql;
    using DMEWorks;
    using DMEWorks.Core;
    using DMEWorks.Data.MySql;
    using DMEWorks.Forms;
    using DMEWorks.Serials;
    using System;
    using System.Collections.Generic;
    using System.Globalization;
    using System.Linq;
    using System.Runtime.CompilerServices;

    public class Session
    {
        public readonly MySqlOdbcDsnInfo DsnInfo;
        public readonly string Username;
        public readonly string Password;
        public readonly string Database;
        public readonly string ConnectionString;
        public readonly short UserId;
        private readonly Dictionary<string, PermissionsStruct> FPermissions;
        private readonly Dictionary<string, string> FVariables;
        public readonly SerialData SerialNumber;
        private const string CrLf = "\r\n";
        private int SessionID;
        private DateTime m_LastCheckChanges;
        private int lastNotificationId;
        private readonly object syncObj;
        private readonly Queue<Notification> ToProcess;
        private readonly HashSet<Notification> ToDismiss;

        public Session(MySqlOdbcDsnInfo dsnInfo, string database, string username, string password)
        {
            string str;
            this.syncObj = new object();
            this.ToProcess = new Queue<Notification>();
            this.ToDismiss = new HashSet<Notification>();
            if (dsnInfo == null)
            {
                MySqlOdbcDsnInfo local1 = dsnInfo;
                throw new ArgumentNullException("dsnInfo");
            }
            this.DsnInfo = dsnInfo;
            if (string.IsNullOrEmpty(database))
            {
                throw new ArgumentException("cannot be empty", "database");
            }
            if (string.IsNullOrEmpty(username))
            {
                throw new ArgumentException("cannot be empty", "username");
            }
            this.Database = database.ToLower();
            this.Username = username;
            string text1 = password;
            if (password == null)
            {
                string local2 = password;
                text1 = string.Empty;
            }
            this.Password = text1;
            this.ConnectionString = this.DsnInfo.Server.GetConnectionString("DMEUser", "DMEPassword", this.Database, InitializationCommand(0));
            this.FPermissions = new Dictionary<string, PermissionsStruct>(StringComparer.InvariantCultureIgnoreCase);
            this.FVariables = new Dictionary<string, string>(StringComparer.InvariantCultureIgnoreCase);
            using (MySqlConnection connection = new MySqlConnection(this.ConnectionString))
            {
                connection.Open();
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = "SELECT ID\r\nFROM tbl_user\r\nWHERE (tbl_user.Login = :login)\r\n  AND (tbl_user.Password = :password)\r\n  AND (BINARY tbl_user.Password = BINARY :password)";
                    command.Parameters.Add("login", MySqlType.VarChar, 100).Value = this.Username;
                    command.Parameters.Add("password", MySqlType.VarChar, 100).Value = this.Password;
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        if (!reader.Read())
                        {
                            throw new UserNotifyException("Either Login or Password is incorrect");
                        }
                        this.UserId = Convert.ToInt16(reader["ID"]);
                    }
                }
                using (MySqlCommand command2 = connection.CreateCommand())
                {
                    command2.CommandText = "SELECT `tbl_object`.`ID`, \r\n       `tbl_object`.`Name`,\r\n       `tbl_permissions`.`ADD_EDIT`,\r\n       `tbl_permissions`.`DELETE`,\r\n       `tbl_permissions`.`PROCESS`,\r\n       `tbl_permissions`.`VIEW`\r\nFROM `tbl_object`\r\n     LEFT JOIN `tbl_permissions` ON `tbl_permissions`.`ObjectID` = `tbl_object`.`ID`\r\n                                AND `tbl_permissions`.`UserID` = " + this.UserId.ToString();
                    using (MySqlDataReader reader2 = command2.ExecuteReader())
                    {
                        while (reader2.Read())
                        {
                            string str2 = Convert.ToString(reader2["Name"]);
                            this.FPermissions[str2] = new PermissionsStruct(NullableConvert.ToBoolean(reader2["ADD_EDIT"], false), NullableConvert.ToBoolean(reader2["DELETE"], false), NullableConvert.ToBoolean(reader2["PROCESS"], false), NullableConvert.ToBoolean(reader2["VIEW"], false));
                        }
                    }
                }
                using (MySqlCommand command3 = connection.CreateCommand())
                {
                    command3.CommandText = "SELECT Name, Value\r\nFROM tbl_variables\r\nWHERE Name IN ('Functions', 'Version', 'Serial')";
                    using (MySqlDataReader reader3 = command3.ExecuteReader())
                    {
                        while (reader3.Read())
                        {
                            string str3 = NullableConvert.ToString(reader3["Name"]);
                            this.FVariables[str3] = NullableConvert.ToString(reader3["Value"]);
                        }
                    }
                }
            }
            this.ConnectionString = this.DsnInfo.Server.GetConnectionString("DMEUser", "DMEPassword", this.Database, InitializationCommand(this.UserId));
            if (this.FVariables.TryGetValue("Serial", out str))
            {
                this.SerialNumber = new SerialData(str);
            }
            else
            {
                this.SerialNumber = new SerialData();
            }
        }

        public void BeginSession()
        {
            using (MySqlConnection connection = this.CreateConnection())
            {
                connection.Open();
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = "SELECT Count(`ID`) as `Count` FROM `tbl_sessions` WHERE `LastUpdateTime` > DATE_SUB(NOW(), INTERVAL 1 MINUTE)";
                    int num = Convert.ToInt32(command.ExecuteScalar());
                    if (!this.SerialNumber.IsDemoSerial() && (this.SerialNumber.MaxCount() <= num))
                    {
                        throw new UserNotifyException("You are tring to exceed limit of connections to server. Try to login later.");
                    }
                }
                using (MySqlCommand command2 = connection.CreateCommand())
                {
                    command2.CommandText = $"INSERT INTO `tbl_sessions` (`UserID`, `LoginTime`, `LastUpdateTime`) VALUES ({this.UserId}, NOW(), NOW())";
                    command2.ExecuteNonQuery();
                }
                using (MySqlCommand command3 = connection.CreateCommand())
                {
                    command3.CommandText = "SELECT LAST_INSERT_ID() as ID";
                    this.SessionID = Convert.ToInt32(command3.ExecuteScalar());
                    this.LastUpdateTime = DateTime.Now;
                }
            }
        }

        public MySqlConnection CreateConnection() => 
            new MySqlConnection(this.ConnectionString);

        public void DismissNotification(Notification notification)
        {
            if (notification != null)
            {
                object syncObj = this.syncObj;
                lock (syncObj)
                {
                    this.ToDismiss.Add(notification);
                }
            }
        }

        public void EndSession()
        {
            using (MySqlConnection connection = this.CreateConnection())
            {
                connection.Open();
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = $"DELETE FROM `tbl_sessions` WHERE `ID` = {this.SessionID}";
                    if (command.ExecuteNonQuery() != 0)
                    {
                        this.LastUpdateTime = DateTime.Now;
                    }
                }
            }
        }

        public string[] GetChangedTables()
        {
            List<string> list = new List<string>(0x10);
            using (MySqlConnection connection = this.CreateConnection())
            {
                using (MySqlCommand command = connection.CreateCommand())
                {
                    MySqlParameter parameter1 = new MySqlParameter("SID", MySqlType.Int);
                    parameter1.Value = this.SessionID;
                    command.Parameters.Add(parameter1);
                    MySqlParameter parameter2 = new MySqlParameter("LastTime", MySqlType.DateTime);
                    parameter2.Value = this.m_LastCheckChanges;
                    command.Parameters.Add(parameter2);
                    command.CommandText = "SELECT TableName\r\nFROM tbl_changes\r\nWHERE :LastTime <= LastUpdateDateTime\r\n  AND SessionID != :SID;\r\nSELECT NOW() as NOW;";
                    connection.Open();
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (true)
                        {
                            if (!reader.Read())
                            {
                                if (!reader.NextResult())
                                {
                                    throw new InvalidOperationException();
                                }
                                if (!reader.Read())
                                {
                                    throw new InvalidOperationException();
                                }
                                this.m_LastCheckChanges = reader.GetDateTime(0);
                                break;
                            }
                            list.Add(reader.GetString(0));
                        }
                    }
                }
            }
            return list.ToArray();
        }

        public Notification GetNotification()
        {
            object syncObj = this.syncObj;
            lock (syncObj)
            {
                return ((0 >= this.ToProcess.Count) ? null : this.ToProcess.Dequeue());
            }
        }

        public PermissionsStruct? GetPermissions(string name)
        {
            PermissionsStruct struct2;
            string key = name;
            if (name == null)
            {
                string local1 = name;
                key = string.Empty;
            }
            if (this.FPermissions.TryGetValue(key, out struct2))
            {
                return new PermissionsStruct?(struct2);
            }
            return null;
        }

        public string GetServerVersion()
        {
            string str;
            using (MySqlConnection connection = this.CreateConnection())
            {
                connection.Open();
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = "SELECT Version()";
                    str = NullableConvert.ToString(command.ExecuteScalar());
                }
            }
            return str;
        }

        public string GetVariable(string name)
        {
            string str;
            string key = name;
            if (name == null)
            {
                string local1 = name;
                key = string.Empty;
            }
            return (!this.FVariables.TryGetValue(key, out str) ? null : str);
        }

        private static string InitializationCommand(int userId) => 
            "SET SESSION\r\n sql_mode='NO_ENGINE_SUBSTITUTION,NO_AUTO_VALUE_ON_ZERO'\r\n,interactive_timeout=28800\r\n,net_read_timeout=28800\r\n,net_write_timeout=28800\r\n,wait_timeout=28800;\r\n" + string.Format((IFormatProvider) CultureInfo.InvariantCulture, "SET @UserId = {0}", userId);

        public void NotifyTablesChanged(string[] tableNames)
        {
            if (tableNames == null)
            {
                throw new ArgumentNullException("tableNames");
            }
            if (tableNames.Length != 0)
            {
                tableNames = tableNames.Distinct<string>(StringComparer.InvariantCultureIgnoreCase).ToArray<string>();
                using (MySqlConnection connection = this.CreateConnection())
                {
                    using (MySqlCommand command = connection.CreateCommand())
                    {
                        MySqlParameter parameter1 = new MySqlParameter("SID", MySqlType.Int);
                        parameter1.Value = this.SessionID;
                        command.Parameters.Add(parameter1);
                        MySqlParameter parameter2 = new MySqlParameter("UID", MySqlType.SmallInt);
                        parameter2.Value = this.UserId;
                        command.Parameters.Add(parameter2);
                        int num = 0;
                        while (true)
                        {
                            if (num >= tableNames.Length)
                            {
                                Func<string, int, string> selector = <>c.<>9__26_0;
                                if (<>c.<>9__26_0 == null)
                                {
                                    Func<string, int, string> local1 = <>c.<>9__26_0;
                                    selector = <>c.<>9__26_0 = (s, i) => $"(:P{i}, :SID, :UID)";
                                }
                                command.CommandText = "REPLACE INTO tbl_changes (TableName, SessionID, LastUpdateUserID) VALUES\r\n" + string.Join(",\r\n", tableNames.Select<string, string>(selector));
                                connection.Open();
                                command.ExecuteNonQuery();
                                break;
                            }
                            MySqlParameter parameter3 = new MySqlParameter($"P{num}", MySqlType.VarChar, 0x40);
                            parameter3.Value = tableNames[num];
                            command.Parameters.Add(parameter3);
                            num++;
                        }
                    }
                }
            }
        }

        public void UpdateSession()
        {
            using (MySqlConnection connection = this.CreateConnection())
            {
                Notification[] notificationArray;
                connection.Open();
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = $"UPDATE `tbl_sessions` SET `LastUpdateTime` = NOW() WHERE `ID` = {this.SessionID}";
                    if (command.ExecuteNonQuery() != 0)
                    {
                        this.LastUpdateTime = DateTime.Now;
                    }
                }
                object syncObj = this.syncObj;
                lock (syncObj)
                {
                    notificationArray = this.ToDismiss.ToArray<Notification>();
                }
                if (notificationArray.Length != 0)
                {
                    using (MySqlCommand command2 = connection.CreateCommand())
                    {
                        command2.CommandText = "DELETE FROM tbl_user_notifications WHERE ID = :ID AND UserID = :UserID";
                        command2.Parameters.Add(new MySqlParameter("ID", MySqlType.Int));
                        MySqlParameter parameter1 = new MySqlParameter("UserID", MySqlType.SmallInt);
                        parameter1.Value = this.UserId;
                        command2.Parameters.Add(parameter1);
                        foreach (Notification notification in notificationArray)
                        {
                            command2.Parameters["ID"].Value = notification.Id;
                            command2.ExecuteNonQuery();
                        }
                    }
                    syncObj = this.syncObj;
                    lock (syncObj)
                    {
                        foreach (Notification notification2 in notificationArray)
                        {
                            this.ToDismiss.Remove(notification2);
                        }
                    }
                }
                using (MySqlCommand command3 = connection.CreateCommand())
                {
                    command3.CommandText = "SELECT ID, Type, Args, Datetime\r\nFROM tbl_user_notifications\r\nWHERE UserID = :UserID\r\n  AND ID > :LastID\r\nORDER BY ID";
                    MySqlParameter parameter2 = new MySqlParameter("UserID", MySqlType.SmallInt);
                    parameter2.Value = this.UserId;
                    command3.Parameters.Add(parameter2);
                    MySqlParameter parameter3 = new MySqlParameter("LastID", MySqlType.Int);
                    parameter3.Value = this.lastNotificationId;
                    command3.Parameters.Add(parameter3);
                    List<Notification> list = new List<Notification>();
                    using (MySqlDataReader reader = command3.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            list.Add(new Notification(Convert.ToInt32(reader[0]), Convert.ToString(reader[1]), Convert.ToString(reader[2]), Convert.ToDateTime(reader[3])));
                        }
                    }
                    Queue<Notification> toProcess = this.ToProcess;
                    lock (toProcess)
                    {
                        foreach (Notification notification3 in list)
                        {
                            this.ToProcess.Enqueue(notification3);
                            if (this.lastNotificationId < notification3.Id)
                            {
                                this.lastNotificationId = notification3.Id;
                            }
                        }
                    }
                }
            }
        }

        public DateTime LastUpdateTime { get; private set; }

        [Serializable, CompilerGenerated]
        private sealed class <>c
        {
            public static readonly Session.<>c <>9 = new Session.<>c();
            public static Func<string, int, string> <>9__26_0;

            internal string <NotifyTablesChanged>b__26_0(string s, int i) => 
                $"(:P{i}, :SID, :UID)";
        }
    }
}

