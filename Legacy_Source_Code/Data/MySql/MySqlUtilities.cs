namespace DMEWorks.Data.MySql
{
    using Devart.Data.MySql;
    using System;
    using System.Collections;
    using System.Collections.Specialized;
    using System.Data;
    using System.Globalization;
    using System.IO;
    using System.Runtime.CompilerServices;
    using System.Text;

    public static class MySqlUtilities
    {
        public static string CommandToString(MySqlCommand cmd)
        {
            if (cmd == null)
            {
                throw new ArgumentNullException("cmd");
            }
            using (StringWriter writer = new StringWriter())
            {
                StringReader reader;
                writer.NewLine = Environment.NewLine;
                foreach (MySqlParameter parameter in cmd.Parameters)
                {
                    try
                    {
                        writer.WriteLine("SET @{0} = {1}", parameter.ParameterName, FormatParameterValue(parameter));
                    }
                    catch
                    {
                    }
                }
                writer.WriteLine();
                if (cmd.CommandType != CommandType.Text)
                {
                    if (cmd.CommandType == CommandType.StoredProcedure)
                    {
                        writer.Write("CALL " + cmd.CommandText + "(");
                        int num = 0;
                        foreach (MySqlParameter parameter2 in cmd.Parameters)
                        {
                            try
                            {
                                if (num == 0)
                                {
                                    writer.Write(",");
                                }
                                writer.Write(" @{0}", parameter2.ParameterName);
                                num++;
                            }
                            catch
                            {
                            }
                        }
                        writer.WriteLine(")");
                    }
                    goto TR_000C;
                }
                else
                {
                    reader = new StringReader(cmd.CommandText);
                }
                goto TR_0010;
            TR_000C:
                return writer.ToString();
            TR_0010:
                try
                {
                    while (true)
                    {
                        string str = reader.ReadLine();
                        if (str != null)
                        {
                            writer.WriteLine(str);
                        }
                        else
                        {
                            goto TR_000C;
                        }
                        break;
                    }
                }
                finally
                {
                    if (reader != null)
                    {
                        reader.Dispose();
                    }
                }
                goto TR_0010;
            }
        }

        public static string EscapeParamName(string ParamName) => 
            ":" + ParamName;

        public static string EscapeString(string value) => 
            (value != null) ? value.Replace("'", "''").Replace(@"\", @"\\") : string.Empty;

        public static int ExecuteCommand(this MySqlCommand cmd, string Command)
        {
            cmd.CommandType = CommandType.Text;
            cmd.CommandText = Command;
            DateTime now = DateTime.Now;
            return cmd.ExecuteNonQuery();
        }

        public static int ExecuteCommand(this MySqlCommand cmd, string Format, object arg) => 
            cmd.ExecuteCommand(string.Format(Format, arg));

        public static int ExecuteCommand(this MySqlCommand cmd, string Format, params object[] args) => 
            cmd.ExecuteCommand(string.Format(Format, args));

        public static int ExecuteCommand(this MySqlCommand cmd, string Format, object arg0, object arg1) => 
            cmd.ExecuteCommand(string.Format(Format, arg0, arg1));

        public static int ExecuteCommand(this MySqlCommand cmd, string Format, object arg0, object arg1, object arg2) => 
            cmd.ExecuteCommand(string.Format(Format, arg0, arg1, arg2));

        public static int ExecuteDelete(this MySqlCommand cmd, string TableName)
        {
            cmd.GenerateDeleteCommand(TableName);
            return cmd.ExecuteNonQuery();
        }

        public static int ExecuteInsert(this MySqlCommand cmd, string TableName)
        {
            cmd.GenerateInsertCommand(TableName);
            return cmd.ExecuteNonQuery();
        }

        public static int ExecuteProcedure(this MySqlCommand cmd, string ProcName)
        {
            cmd.GenerateProcedureCommand(ProcName);
            return cmd.ExecuteNonQuery();
        }

        public static int ExecuteUpdate(this MySqlCommand cmd, string TableName, string[] WhereParameters)
        {
            cmd.GenerateUpdateCommand(TableName, WhereParameters);
            return cmd.ExecuteNonQuery();
        }

        public static void FillTable(MySqlDataAdapter da, DataTable table)
        {
            DateTime now = DateTime.Now;
            da.Fill(table);
        }

        private static string FormatParameterValue(MySqlParameter param)
        {
            object obj2 = param.Value;
            string str = obj2 as string;
            if (str != null)
            {
                return ("'" + str.Replace("'", "''") + "'");
            }
            if (obj2 as bool)
            {
                return (((bool) obj2) ? "1" : "0");
            }
            if (obj2 is DateTime)
            {
                return ((DateTime) obj2).ToString("yyyy-MM-dd HH:mm:ss.fff", CultureInfo.InvariantCulture);
            }
            if (!(obj2 is sbyte) && (!(obj2 is short) && (!(obj2 is int) && (!(obj2 is long) && (!(obj2 is byte) && (!(obj2 is ushort) && (!(obj2 is uint) && (!(obj2 is ulong) && (!(obj2 is double) && (!(obj2 is decimal) && !(obj2 is float)))))))))))
            {
                throw new NotSupportedException("Unsupported value type");
            }
            return Convert.ToString(obj2, CultureInfo.InvariantCulture);
        }

        public static void GenerateDeleteCommand(this MySqlCommand cmd, string TableName)
        {
            if (cmd == null)
            {
                throw new ArgumentNullException("cmd");
            }
            StringBuilder builder = new StringBuilder();
            builder.Append("DELETE FROM ").Append(TableName).Append(" WHERE (1 = 1)");
            for (int i = 0; i < cmd.Parameters.Count; i++)
            {
                MySqlParameter parameter = cmd.Parameters[i];
                string[] textArray1 = new string[] { " AND (", QuoteIdentifier(parameter.ParameterName), " = ", EscapeParamName(parameter.ParameterName), ")" };
                builder.Append(string.Concat(textArray1));
            }
            cmd.CommandType = CommandType.Text;
            cmd.CommandText = builder.ToString();
        }

        public static void GenerateInsertCommand(this MySqlCommand cmd, string TableName)
        {
            if (cmd == null)
            {
                throw new ArgumentNullException("cmd");
            }
            StringBuilder builder = new StringBuilder();
            builder.Append("INSERT INTO ").Append(TableName).Append(" (");
            for (int i = 0; i < cmd.Parameters.Count; i++)
            {
                if (0 < i)
                {
                    builder.Append(", ");
                }
                builder.Append(QuoteIdentifier(cmd.Parameters[i].ParameterName));
            }
            builder.Append(") VALUES (");
            for (int j = 0; j < cmd.Parameters.Count; j++)
            {
                if (0 < j)
                {
                    builder.Append(", ");
                }
                builder.Append(EscapeParamName(cmd.Parameters[j].ParameterName));
            }
            builder.Append(")");
            cmd.CommandType = CommandType.Text;
            cmd.CommandText = builder.ToString();
        }

        public static void GenerateProcedureCommand(this MySqlCommand cmd, string ProcName)
        {
            if (cmd == null)
            {
                throw new ArgumentNullException("cmd");
            }
            cmd.CommandType = CommandType.StoredProcedure;
            cmd.CommandText = ProcName;
        }

        public static void GenerateUpdateCommand(this MySqlCommand cmd, string tableName, string[] whereParameters)
        {
            if (cmd == null)
            {
                throw new ArgumentNullException("cmd");
            }
            Hashtable hashtable = CollectionsUtil.CreateCaseInsensitiveHashtable();
            if (whereParameters != null)
            {
                for (int k = 0; k < whereParameters.Length; k++)
                {
                    hashtable[whereParameters[k]] = whereParameters[k];
                }
            }
            StringBuilder builder = new StringBuilder();
            builder.Append("UPDATE ").Append(tableName).Append(" SET ");
            int length = builder.Length;
            for (int i = 0; i < cmd.Parameters.Count; i++)
            {
                MySqlParameter parameter = cmd.Parameters[i];
                if (!hashtable.ContainsKey(parameter.ParameterName))
                {
                    if (length < builder.Length)
                    {
                        builder.Append(", ");
                    }
                    builder.Append(QuoteIdentifier(parameter.ParameterName) + " = " + EscapeParamName(parameter.ParameterName));
                }
            }
            builder.Append(" WHERE (1 = 1)");
            for (int j = 0; j < cmd.Parameters.Count; j++)
            {
                MySqlParameter parameter2 = cmd.Parameters[j];
                if (hashtable.ContainsKey(parameter2.ParameterName))
                {
                    string[] textArray1 = new string[] { " AND (", QuoteIdentifier(parameter2.ParameterName), " = ", EscapeParamName(parameter2.ParameterName), ")" };
                    builder.Append(string.Concat(textArray1));
                }
            }
            cmd.CommandType = CommandType.Text;
            cmd.CommandText = builder.ToString();
        }

        public static int GetLastIdentity(this MySqlCommand cmd)
        {
            cmd.CommandText = "SELECT LAST_INSERT_ID()";
            return Convert.ToInt32(cmd.ExecuteScalar());
        }

        public static string QuoteIdentifier(string identifier) => 
            "`" + identifier + "`";

        public static string QuoteString(string value)
        {
            string text1 = value;
            if (value == null)
            {
                string local1 = value;
                text1 = "";
            }
            return ("'" + text1.Replace("'", "''").Replace(@"\", @"\\") + "'");
        }
    }
}

