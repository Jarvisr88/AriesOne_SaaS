namespace DMEWorks.Data.MySql
{
    using Devart.Data.MySql;
    using DMEWorks.Expressions;
    using System;
    using System.Runtime.CompilerServices;

    public class QueryExpression : PrimitiveExpression
    {
        public QueryExpression(string text, MySqlType dbType)
        {
            this.<ExpressionText>k__BackingField = text;
            this.<DbType>k__BackingField = dbType;
        }

        public string ExpressionText { get; }

        public MySqlType DbType { get; }

        public override System.Type Type
        {
            get
            {
                switch (this.DbType)
                {
                    case MySqlType.BigInt:
                        return typeof(long);

                    case MySqlType.Binary:
                    case MySqlType.VarBinary:
                        return typeof(byte[]);

                    case MySqlType.Bit:
                        return typeof(bool);

                    case MySqlType.Blob:
                    case MySqlType.Geometry:
                        return typeof(byte[]);

                    case MySqlType.Char:
                    case MySqlType.VarChar:
                        return typeof(string);

                    case MySqlType.Date:
                    case MySqlType.DateTime:
                    case MySqlType.TimeStamp:
                        return typeof(DateTime);

                    case MySqlType.Decimal:
                        return typeof(decimal);

                    case MySqlType.Double:
                        return typeof(double);

                    case MySqlType.Float:
                        return typeof(float);

                    case MySqlType.Int:
                        return typeof(int);

                    case MySqlType.SmallInt:
                        return typeof(short);

                    case MySqlType.Text:
                        return typeof(string);

                    case MySqlType.Time:
                        return typeof(TimeSpan);

                    case MySqlType.TinyInt:
                        return typeof(byte);

                    case MySqlType.Year:
                        return typeof(short);

                    case MySqlType.Guid:
                        return typeof(Guid);
                }
                return typeof(object);
            }
        }
    }
}

