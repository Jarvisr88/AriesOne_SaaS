namespace DMEWorks.Data.MySql
{
    using Microsoft.Win32;
    using System;
    using System.Collections.Generic;
    using System.Runtime.CompilerServices;

    public sealed class MySqlOdbcDsnInfo
    {
        private const string odbcKey = @"SOFTWARE\ODBC\ODBC.INI\";
        private static Dictionary<string, MySqlOdbcDsnInfo> FServers = new Dictionary<string, MySqlOdbcDsnInfo>(StringComparer.OrdinalIgnoreCase);

        private MySqlOdbcDsnInfo(string dsnName, RegistryKey dsnKey)
        {
            int num;
            int num2;
            if (string.IsNullOrEmpty(dsnName))
            {
                throw new ArgumentException("Cannot be empty", "dsnName");
            }
            if (dsnKey == null)
            {
                throw new ArgumentNullException("dsnKey");
            }
            this.<DsnName>k__BackingField = dsnName;
            string text1 = dsnKey.GetValue("UID") as string;
            string text5 = text1;
            if (text1 == null)
            {
                string local1 = text1;
                string text2 = dsnKey.GetValue("User") as string;
                text5 = text2;
                if (text2 == null)
                {
                    string local2 = text2;
                    text5 = string.Empty;
                }
            }
            this.<Username>k__BackingField = text5;
            string text3 = dsnKey.GetValue("PWD") as string;
            string text6 = text3;
            if (text3 == null)
            {
                string local3 = text3;
                string text4 = dsnKey.GetValue("Password") as string;
                text6 = text4;
                if (text4 == null)
                {
                    string local4 = text4;
                    text6 = string.Empty;
                }
            }
            this.<Password>k__BackingField = text6;
            string server = Convert.ToString(dsnKey.GetValue("SERVER"));
            if (!int.TryParse(Convert.ToString(dsnKey.GetValue("PORT")), out num))
            {
                num = 0xcea;
            }
            if (!int.TryParse(Convert.ToString(dsnKey.GetValue("COMPRESSED_PROTO")), out num2))
            {
                num2 = 0;
            }
            this.<Server>k__BackingField = new MySqlServerInfo(server, num, num2 != 0);
        }

        private static MySqlOdbcDsnInfo FindInfo(string dsnName)
        {
            RegistryKey[] keyArray = new RegistryKey[] { Registry.CurrentUser, Registry.LocalMachine };
            int index = 0;
            while (true)
            {
                while (true)
                {
                    if (index >= keyArray.Length)
                    {
                        return null;
                    }
                    using (RegistryKey key = keyArray[index].OpenSubKey(@"SOFTWARE\ODBC\ODBC.INI\" + dsnName))
                    {
                        if (key == null)
                        {
                            break;
                        }
                        return new MySqlOdbcDsnInfo(dsnName, key);
                    }
                }
                index++;
            }
        }

        public static MySqlOdbcDsnInfo GetDsn(string dsnName)
        {
            if (dsnName == null)
            {
                throw new ArgumentNullException("dsnName");
            }
            if (dsnName.Length == 0)
            {
                throw new ArgumentException("is empty", "dsnName");
            }
            lock (FServers)
            {
                MySqlOdbcDsnInfo info;
                if (!FServers.TryGetValue(dsnName, out info))
                {
                    FServers[dsnName] = info = FindInfo(dsnName);
                }
                return info;
            }
        }

        public static MySqlOdbcDsnInfo[] GetDsns()
        {
            List<MySqlOdbcDsnInfo> list = new List<MySqlOdbcDsnInfo>();
            RegistryKey[] keyArray1 = new RegistryKey[] { Registry.CurrentUser, Registry.LocalMachine };
            foreach (RegistryKey key in keyArray1)
            {
                using (RegistryKey key2 = key.OpenSubKey(@"SOFTWARE\ODBC\ODBC.INI\ODBC Data Sources"))
                {
                    if (key2 != null)
                    {
                        foreach (string str in key2.GetValueNames())
                        {
                            if ((Convert.ToString(key2.GetValue(str, "")) ?? "").StartsWith("MySQL ODBC", StringComparison.OrdinalIgnoreCase))
                            {
                                using (RegistryKey key3 = key.OpenSubKey(@"SOFTWARE\ODBC\ODBC.INI\" + str))
                                {
                                    if (key3 != null)
                                    {
                                        list.Add(new MySqlOdbcDsnInfo(str, key3));
                                    }
                                }
                            }
                        }
                    }
                }
            }
            return list.ToArray();
        }

        public override string ToString() => 
            this.DsnName;

        public string DsnName { get; }

        public string Username { get; }

        public string Password { get; }

        public MySqlServerInfo Server { get; }
    }
}

