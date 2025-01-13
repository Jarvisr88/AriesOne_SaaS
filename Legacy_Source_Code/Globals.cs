namespace DMEWorks
{
    using Devart.Data.MySql;
    using DMEWorks.Core;
    using DMEWorks.Core.Extensions;
    using DMEWorks.Data;
    using DMEWorks.Data.MySql;
    using DMEWorks.Serials;
    using System;
    using System.Collections.Generic;
    using System.Data;
    using System.Runtime.CompilerServices;
    using System.Threading;

    public static class Globals
    {
        private static Thread m_worker;
        private static SessionWrapper m_wrapper;

        public static event EventHandler<DatabaseChangedEventArgs> DatabaseChanged;

        public static event EventHandler Disconnected;

        public static event EventHandler Disconnecting;

        public static MySqlConnection CreateConnection() => 
            new MySqlConnection(ConnectionString);

        public static void DismissNotification(Notification notification)
        {
            if (notification != null)
            {
                Invoke(w => w.Session.DismissNotification(notification));
            }
        }

        private static void DoWork()
        {
            DateTime minValue = DateTime.MinValue;
            DateTime time2 = DateTime.MinValue;
            while (true)
            {
                if (minValue < DateTime.UtcNow)
                {
                    SessionWrapper wrapper = m_wrapper;
                    if (wrapper != null)
                    {
                        try
                        {
                            DateTime now = DateTime.Now;
                            if (DateTime.Compare(wrapper.Session.LastUpdateTime, now.AddMinutes(-2.0)) < 0)
                            {
                                OnDisconnecting();
                            }
                            else
                            {
                                wrapper.Session.UpdateSession();
                            }
                        }
                        catch (Exception exception1)
                        {
                            TraceHelper.TraceException(exception1);
                        }
                    }
                    minValue = DateTime.UtcNow.AddSeconds(15.0);
                }
                if (time2 < DateTime.UtcNow)
                {
                    SessionWrapper wrapper = m_wrapper;
                    if (wrapper != null)
                    {
                        try
                        {
                            string[] changedTables = wrapper.Session.GetChangedTables();
                            if (changedTables.Length != 0)
                            {
                                OnDatabaseChanged(new DatabaseChangedEventArgs(changedTables));
                            }
                        }
                        catch (Exception exception2)
                        {
                            TraceHelper.TraceException(exception2);
                        }
                    }
                    time2 = DateTime.UtcNow.AddSeconds(2.0);
                }
                Thread.Sleep(100);
            }
        }

        public static object ExecuteScalar(string commandText, params MySqlParameter[] parameters) => 
            ExecuteScalar(commandText, CommandType.Text, parameters);

        public static object ExecuteScalar(string commandText, CommandType commandType, params MySqlParameter[] parameters)
        {
            object obj2;
            using (MySqlConnection connection = CreateConnection())
            {
                using (MySqlCommand command = connection.CreateCommand())
                {
                    command.CommandText = commandText;
                    command.CommandType = commandType;
                    if ((parameters != null) && (parameters.Length != 0))
                    {
                        command.Parameters.AddRange(parameters);
                    }
                    connection.Open();
                    obj2 = command.ExecuteScalar();
                }
            }
            return obj2;
        }

        public static string GetCompanyVariable(string name) => 
            Invoke<string>(w => w.Session.GetVariable(name), null);

        public static Notification GetNotification() => 
            Invoke<Notification>(<>c.<>9__75_0 ??= w => w.Session.GetNotification(), null);

        public static PermissionsStruct? GetUserPermissions(string name)
        {
            PermissionsStruct? nullable = null;
            return Invoke<PermissionsStruct?>(w => w.Session.GetPermissions(name), nullable);
        }

        private static void Invoke(Action<SessionWrapper> action)
        {
            SessionWrapper wrapper = m_wrapper;
            if (wrapper != null)
            {
                action(wrapper);
            }
        }

        private static T Invoke<T>(Func<Location, T> func, T @default)
        {
            SessionWrapper wrapper = m_wrapper;
            if (wrapper != null)
            {
                Location arg = wrapper.Location;
                if (arg != null)
                {
                    return func(arg);
                }
            }
            return @default;
        }

        private static T Invoke<T>(Func<SessionWrapper, T> func, T @default)
        {
            SessionWrapper arg = m_wrapper;
            return ((arg != null) ? func(arg) : @default);
        }

        public static void Login(MySqlOdbcDsnInfo dsnInfo, string database, string username, string password)
        {
            object[] args = new object[] { DateTime.Now };
            TraceHelper.TraceInfo("{0:yyyy-MM-dd HH:mm:ss} Login", args);
            if (m_wrapper != null)
            {
                throw new Exception("Cannot perform requested operation (Login) on open connection");
            }
            try
            {
                m_wrapper = SessionWrapper.Create(dsnInfo, database, username, password);
            }
            catch (Exception)
            {
                throw;
            }
        }

        public static void Logoff()
        {
            object[] args = new object[] { DateTime.Now };
            TraceHelper.TraceInfo("{0:yyyy-MM-dd HH:mm:ss} Logoff", args);
            if (m_wrapper != null)
            {
                OnDisconnected();
                m_wrapper.Session.EndSession();
                m_wrapper = null;
            }
        }

        public static void NotifyTablesChanged(string[] tableNames)
        {
            SessionWrapper wrapper = m_wrapper;
            if (wrapper != null)
            {
                try
                {
                    wrapper.Session.NotifyTablesChanged(tableNames);
                }
                catch (Exception exception1)
                {
                    TraceHelper.TraceException(exception1);
                }
            }
        }

        private static void OnDatabaseChanged(DatabaseChangedEventArgs args)
        {
            EventHandler<DatabaseChangedEventArgs> databaseChanged = DatabaseChanged;
            if (databaseChanged != null)
            {
                databaseChanged(null, args);
            }
        }

        private static void OnDisconnected()
        {
            EventHandler disconnected = Disconnected;
            if (disconnected != null)
            {
                disconnected(null, EventArgs.Empty);
            }
        }

        private static void OnDisconnecting()
        {
            EventHandler disconnecting = Disconnecting;
            if (disconnecting != null)
            {
                disconnecting(null, EventArgs.Empty);
            }
        }

        public static void ReloadCompany()
        {
            Invoke(<>c.<>9__24_0 ??= w => w.ReloadCompany());
        }

        public static void StartBackgroundWorker()
        {
            if (m_worker == null)
            {
                Thread thread1 = new Thread(new ThreadStart(Globals.DoWork));
                thread1.IsBackground = true;
                thread1.Name = "Background worker";
                m_worker = thread1;
                m_worker.Start();
            }
        }

        public static bool AutoGenerateAccountNumbers =>
            Invoke<bool>(<>c.<>9__27_0 ??= w => w.Company.AutoGenerateAccountNumbers, false);

        public static bool AutoReorderInventory =>
            Invoke<bool>(<>c.<>9__29_0 ??= w => w.Company.AutoReorderInventory, false);

        public static bool ShowQuantityOnHand =>
            Invoke<bool>(<>c.<>9__31_0 ??= w => w.Company.ShowQuantityOnHand, false);

        public static string CompanyDatabase =>
            Invoke<string>(<>c.<>9__33_0 ??= w => w.Session.Database, string.Empty);

        public static Uri CompanyImagingUri =>
            Invoke<Uri>(<>c.<>9__35_0 ??= w => w.Company.ImagingUri, null);

        public static string CompanyName =>
            Invoke<string>(<>c.<>9__37_0 ??= w => w.Company.Name, string.Empty);

        public static MySqlServerInfo CompanyServer =>
            Invoke<MySqlServerInfo>(<>c.<>9__39_0 ??= w => w.Session.DsnInfo.Server, null);

        public static short CompanyUserID =>
            Invoke<short>(<>c.<>9__41_0 ??= w => w.Session.UserId, 0);

        public static string CompanyUserName =>
            Invoke<string>(<>c.<>9__43_0 ??= w => w.Session.Username, string.Empty);

        public static int? CompanyPOSTypeID
        {
            get
            {
                int? nullable = null;
                return Invoke<int?>(<>c.<>9__46_0 ??= w => w.Company.POSTypeID, nullable);
            }
        }

        public static int? CompanyWarehouseID
        {
            get
            {
                int? nullable = null;
                return Invoke<int?>(<>c.<>9__48_0 ??= w => w.Company.WarehouseID, nullable);
            }
        }

        public static int? CompanyTaxRateID
        {
            get
            {
                int? nullable = null;
                return Invoke<int?>(<>c.<>9__50_0 ??= w => w.Company.TaxRateID, nullable);
            }
        }

        public static int? CompanyOrderSurveyID
        {
            get
            {
                int? nullable = null;
                return Invoke<int?>(<>c.<>9__52_0 ??= w => w.Company.OrderSurveyID, nullable);
            }
        }

        public static bool Connected =>
            m_wrapper != null;

        public static string ConnectionString =>
            Invoke<string>(<>c.<>9__56_0 ??= w => w.Session.ConnectionString, string.Empty);

        public static int? LocationID
        {
            get
            {
                int? nullable = null;
                return Invoke<int?>(<>c.<>9__58_0 ??= w => w.LocationID, nullable);
            }
            set => 
                Invoke(w => w.LocationID = value);
        }

        public static string LocationName =>
            Invoke<string>(<>c.<>9__61_0 ??= w => ((w.Location != null) ? w.Location.Name : string.Empty), string.Empty);

        public static int? LocationPOSTypeID
        {
            get
            {
                int? nullable = null;
                return Invoke<int?>(<>c.<>9__63_0 ??= l => l.POSTypeID, nullable);
            }
        }

        public static int? LocationWarehouseID
        {
            get
            {
                int? nullable = null;
                return Invoke<int?>(<>c.<>9__65_0 ??= l => l.WarehouseID, nullable);
            }
        }

        public static int? LocationTaxRateID
        {
            get
            {
                int? nullable = null;
                return Invoke<int?>(<>c.<>9__67_0 ??= l => l.TaxRateID, nullable);
            }
        }

        public static string ODBCDSN =>
            Invoke<string>(<>c.<>9__69_0 ??= w => w.Session.DsnInfo.DsnName, null);

        public static SerialData SerialNumber
        {
            get
            {
                SerialData data = new SerialData();
                return Invoke<SerialData>(<>c.<>9__71_0 ??= w => w.Session.SerialNumber, data);
            }
        }

        [Serializable, CompilerGenerated]
        private sealed class <>c
        {
            public static readonly Globals.<>c <>9 = new Globals.<>c();
            public static Action<Globals.SessionWrapper> <>9__24_0;
            public static Func<Globals.SessionWrapper, bool> <>9__27_0;
            public static Func<Globals.SessionWrapper, bool> <>9__29_0;
            public static Func<Globals.SessionWrapper, bool> <>9__31_0;
            public static Func<Globals.SessionWrapper, string> <>9__33_0;
            public static Func<Globals.SessionWrapper, Uri> <>9__35_0;
            public static Func<Globals.SessionWrapper, string> <>9__37_0;
            public static Func<Globals.SessionWrapper, MySqlServerInfo> <>9__39_0;
            public static Func<Globals.SessionWrapper, short> <>9__41_0;
            public static Func<Globals.SessionWrapper, string> <>9__43_0;
            public static Func<Globals.SessionWrapper, int?> <>9__46_0;
            public static Func<Globals.SessionWrapper, int?> <>9__48_0;
            public static Func<Globals.SessionWrapper, int?> <>9__50_0;
            public static Func<Globals.SessionWrapper, int?> <>9__52_0;
            public static Func<Globals.SessionWrapper, string> <>9__56_0;
            public static Func<Globals.SessionWrapper, int?> <>9__58_0;
            public static Func<Globals.SessionWrapper, string> <>9__61_0;
            public static Func<Location, int?> <>9__63_0;
            public static Func<Location, int?> <>9__65_0;
            public static Func<Location, int?> <>9__67_0;
            public static Func<Globals.SessionWrapper, string> <>9__69_0;
            public static Func<Globals.SessionWrapper, SerialData> <>9__71_0;
            public static Func<Globals.SessionWrapper, Notification> <>9__75_0;

            internal bool <get_AutoGenerateAccountNumbers>b__27_0(Globals.SessionWrapper w) => 
                w.Company.AutoGenerateAccountNumbers;

            internal bool <get_AutoReorderInventory>b__29_0(Globals.SessionWrapper w) => 
                w.Company.AutoReorderInventory;

            internal string <get_CompanyDatabase>b__33_0(Globals.SessionWrapper w) => 
                w.Session.Database;

            internal Uri <get_CompanyImagingUri>b__35_0(Globals.SessionWrapper w) => 
                w.Company.ImagingUri;

            internal string <get_CompanyName>b__37_0(Globals.SessionWrapper w) => 
                w.Company.Name;

            internal int? <get_CompanyOrderSurveyID>b__52_0(Globals.SessionWrapper w) => 
                w.Company.OrderSurveyID;

            internal int? <get_CompanyPOSTypeID>b__46_0(Globals.SessionWrapper w) => 
                w.Company.POSTypeID;

            internal MySqlServerInfo <get_CompanyServer>b__39_0(Globals.SessionWrapper w) => 
                w.Session.DsnInfo.Server;

            internal int? <get_CompanyTaxRateID>b__50_0(Globals.SessionWrapper w) => 
                w.Company.TaxRateID;

            internal short <get_CompanyUserID>b__41_0(Globals.SessionWrapper w) => 
                w.Session.UserId;

            internal string <get_CompanyUserName>b__43_0(Globals.SessionWrapper w) => 
                w.Session.Username;

            internal int? <get_CompanyWarehouseID>b__48_0(Globals.SessionWrapper w) => 
                w.Company.WarehouseID;

            internal string <get_ConnectionString>b__56_0(Globals.SessionWrapper w) => 
                w.Session.ConnectionString;

            internal int? <get_LocationID>b__58_0(Globals.SessionWrapper w) => 
                w.LocationID;

            internal string <get_LocationName>b__61_0(Globals.SessionWrapper w) => 
                (w.Location != null) ? w.Location.Name : string.Empty;

            internal int? <get_LocationPOSTypeID>b__63_0(Location l) => 
                l.POSTypeID;

            internal int? <get_LocationTaxRateID>b__67_0(Location l) => 
                l.TaxRateID;

            internal int? <get_LocationWarehouseID>b__65_0(Location l) => 
                l.WarehouseID;

            internal string <get_ODBCDSN>b__69_0(Globals.SessionWrapper w) => 
                w.Session.DsnInfo.DsnName;

            internal SerialData <get_SerialNumber>b__71_0(Globals.SessionWrapper w) => 
                w.Session.SerialNumber;

            internal bool <get_ShowQuantityOnHand>b__31_0(Globals.SessionWrapper w) => 
                w.Company.ShowQuantityOnHand;

            internal Notification <GetNotification>b__75_0(Globals.SessionWrapper w) => 
                w.Session.GetNotification();

            internal void <ReloadCompany>b__24_0(Globals.SessionWrapper w)
            {
                w.ReloadCompany();
            }
        }

        public sealed class DatabaseChangedEventArgs : EventArgs
        {
            public DatabaseChangedEventArgs(string[] tableName)
            {
                if (tableName == null)
                {
                    string[] local1 = tableName;
                    throw new ArgumentNullException("tableName");
                }
                this.<TableNames>k__BackingField = tableName;
            }

            public IReadOnlyList<string> TableNames { get; }
        }

        private class SessionWrapper
        {
            private SessionWrapper(DMEWorks.Data.Session session, DMEWorks.Data.Company company)
            {
                if (session == null)
                {
                    DMEWorks.Data.Session local1 = session;
                    throw new ArgumentNullException("session");
                }
                this.<Session>k__BackingField = session;
                if (company == null)
                {
                    DMEWorks.Data.Company local2 = company;
                    throw new ArgumentNullException("company");
                }
                this.Company = company;
                this.Location = null;
            }

            public static Globals.SessionWrapper Create(MySqlOdbcDsnInfo dsnInfo, string database, string username, string password)
            {
                DMEWorks.Data.Session session = new DMEWorks.Data.Session(dsnInfo, database, username, password);
                TraceHelper.TraceInfo("Server version: " + session.GetServerVersion());
                session.BeginSession();
                return new Globals.SessionWrapper(session, new DMEWorks.Data.Company(session));
            }

            public void ReloadCompany()
            {
                this.Company = new DMEWorks.Data.Company(this.Session);
            }

            public DMEWorks.Data.Session Session { get; }

            public DMEWorks.Data.Company Company { get; private set; }

            public DMEWorks.Data.Location Location { get; private set; }

            public int? LocationID
            {
                get
                {
                    DMEWorks.Data.Location location = this.Location;
                    if (location != null)
                    {
                        return new int?(location.ID);
                    }
                    return null;
                }
                set
                {
                    DMEWorks.Data.Location location = null;
                    if (value != null)
                    {
                        using (MySqlConnection connection = this.Session.CreateConnection())
                        {
                            using (MySqlCommand command = connection.CreateCommand())
                            {
                                command.CommandText = "SELECT * FROM tbl_location WHERE ID = :ID";
                                MySqlParameter parameter1 = new MySqlParameter("ID", MySqlType.Int);
                                parameter1.Value = value.Value;
                                command.Parameters.Add(parameter1);
                                connection.Open();
                                Func<IDataRecord, DMEWorks.Data.Location> selector = <>c.<>9__15_0;
                                if (<>c.<>9__15_0 == null)
                                {
                                    Func<IDataRecord, DMEWorks.Data.Location> local1 = <>c.<>9__15_0;
                                    selector = <>c.<>9__15_0 = delegate (IDataRecord r) {
                                        DMEWorks.Data.Location location1 = new DMEWorks.Data.Location();
                                        location1.ID = r.GetInt32("ID").Value;
                                        location1.Name = r.GetString("Name");
                                        location1.POSTypeID = r.GetInt32("POSTypeID");
                                        location1.WarehouseID = r.GetInt32("WarehouseID");
                                        location1.TaxRateID = r.GetInt32("TaxRateID");
                                        return location1;
                                    };
                                }
                                List<DMEWorks.Data.Location> list = command.ExecuteList<DMEWorks.Data.Location>(selector);
                                location = (0 < list.Count) ? list[0] : null;
                            }
                        }
                    }
                    this.Location = location;
                }
            }

            [Serializable, CompilerGenerated]
            private sealed class <>c
            {
                public static readonly Globals.SessionWrapper.<>c <>9 = new Globals.SessionWrapper.<>c();
                public static Func<IDataRecord, Location> <>9__15_0;

                internal Location <set_LocationID>b__15_0(IDataRecord r)
                {
                    Location location1 = new Location();
                    location1.ID = r.GetInt32("ID").Value;
                    location1.Name = r.GetString("Name");
                    location1.POSTypeID = r.GetInt32("POSTypeID");
                    location1.WarehouseID = r.GetInt32("WarehouseID");
                    location1.TaxRateID = r.GetInt32("TaxRateID");
                    return location1;
                }
            }
        }
    }
}

