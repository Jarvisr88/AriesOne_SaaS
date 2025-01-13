namespace SODA
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Runtime.CompilerServices;
    using System.Text;

    public class SoqlQuery
    {
        public static readonly string Delimiter = ",";
        public static readonly string SelectKey = "$select";
        public static readonly string WhereKey = "$where";
        public static readonly string OrderKey = "$order";
        public static readonly string GroupKey = "$group";
        public static readonly string LimitKey = "$limit";
        public static readonly string OffsetKey = "$offset";
        public static readonly string SearchKey = "$q";
        public static readonly string[] DefaultSelect = new string[] { "*" };
        public static readonly SoqlOrderDirection DefaultOrderDirection = SoqlOrderDirection.ASC;
        public static readonly string[] DefaultOrder = new string[] { ":id" };
        public static readonly int MaximumLimit = 0xc350;

        public SoqlQuery()
        {
            this.SelectColumns = DefaultSelect;
            this.SelectColumnAliases = new string[0];
            this.OrderByColumns = DefaultOrder;
            this.OrderDirection = DefaultOrderDirection;
        }

        public SoqlQuery As(params string[] columnAliases)
        {
            string[] textArray1 = getNonEmptyValues(columnAliases);
            string[] source = textArray1;
            if (textArray1 == null)
            {
                string[] local1 = textArray1;
                source = new string[0];
            }
            this.SelectColumnAliases = source.Select<string, string>((<>c.<>9__51_0 ??= a => a.ToLower())).ToArray<string>();
            return this;
        }

        public SoqlQuery FullTextSearch(string searchText)
        {
            this.SearchText = searchText;
            return this;
        }

        public SoqlQuery FullTextSearch(string format, params object[] args) => 
            this.FullTextSearch(string.Format(format, args));

        private static string[] getNonEmptyValues(IEnumerable<string> source)
        {
            if (source != null)
            {
                Func<string, bool> predicate = <>c.<>9__61_0;
                if (<>c.<>9__61_0 == null)
                {
                    Func<string, bool> local1 = <>c.<>9__61_0;
                    predicate = <>c.<>9__61_0 = s => !string.IsNullOrEmpty(s);
                }
                if (source.Any<string>(predicate))
                {
                    Func<string, bool> func2 = <>c.<>9__61_1;
                    if (<>c.<>9__61_1 == null)
                    {
                        Func<string, bool> local2 = <>c.<>9__61_1;
                        func2 = <>c.<>9__61_1 = s => !string.IsNullOrEmpty(s);
                    }
                    return source.Where<string>(func2).ToArray<string>();
                }
            }
            return null;
        }

        public SoqlQuery Group(params string[] columns)
        {
            this.GroupByColumns = getNonEmptyValues(columns);
            return this;
        }

        public SoqlQuery Limit(int limit)
        {
            if (limit <= 0)
            {
                throw new ArgumentOutOfRangeException("limit");
            }
            this.LimitValue = Math.Min(limit, MaximumLimit);
            return this;
        }

        public SoqlQuery Offset(int offset)
        {
            if (offset < 0)
            {
                throw new ArgumentOutOfRangeException("offset");
            }
            this.OffsetValue = offset;
            return this;
        }

        public SoqlQuery Order(params string[] columns) => 
            this.Order(DefaultOrderDirection, columns);

        public SoqlQuery Order(SoqlOrderDirection direction, params string[] columns)
        {
            this.OrderDirection = direction;
            string[] textArray1 = getNonEmptyValues(columns);
            string[] defaultOrder = textArray1;
            if (textArray1 == null)
            {
                string[] local1 = textArray1;
                defaultOrder = DefaultOrder;
            }
            this.OrderByColumns = defaultOrder;
            return this;
        }

        public SoqlQuery Select(params string[] columns)
        {
            string[] textArray1 = getNonEmptyValues(columns);
            string[] defaultSelect = textArray1;
            if (textArray1 == null)
            {
                string[] local1 = textArray1;
                defaultSelect = DefaultSelect;
            }
            this.SelectColumns = defaultSelect;
            return this;
        }

        public override string ToString()
        {
            StringBuilder builder = new StringBuilder();
            builder.AppendFormat("{0}=", SelectKey);
            if ((this.SelectColumns.Length == 1) && (this.SelectColumns[0] == "*"))
            {
                builder.Append(this.SelectColumns[0]);
            }
            else
            {
                Func<string, string, string> resultSelector = <>c.<>9__49_0;
                if (<>c.<>9__49_0 == null)
                {
                    Func<string, string, string> local1 = <>c.<>9__49_0;
                    resultSelector = <>c.<>9__49_0 = (c, a) => $"{c} AS {a}";
                }
                List<string> values = this.SelectColumns.Zip<string, string, string>(this.SelectColumnAliases, resultSelector).ToList<string>();
                if (this.SelectColumns.Length > this.SelectColumnAliases.Length)
                {
                    values.AddRange(this.SelectColumns.Skip<string>(this.SelectColumnAliases.Length));
                }
                builder.Append(string.Join(Delimiter, values));
            }
            builder.AppendFormat("&{0}={1} {2}", OrderKey, string.Join(Delimiter, this.OrderByColumns), this.OrderDirection);
            if (!string.IsNullOrEmpty(this.WhereClause))
            {
                builder.AppendFormat("&{0}={1}", WhereKey, this.WhereClause);
            }
            if ((this.GroupByColumns != null) && this.GroupByColumns.Any<string>())
            {
                builder.AppendFormat("&{0}={1}", GroupKey, string.Join(Delimiter, this.GroupByColumns));
            }
            if (this.OffsetValue > 0)
            {
                builder.AppendFormat("&{0}={1}", OffsetKey, this.OffsetValue);
            }
            if (this.LimitValue > 0)
            {
                builder.AppendFormat("&{0}={1}", LimitKey, this.LimitValue);
            }
            if (!string.IsNullOrEmpty(this.SearchText))
            {
                builder.AppendFormat("&{0}={1}", SearchKey, this.SearchText);
            }
            return builder.ToString();
        }

        public SoqlQuery Where(string predicate)
        {
            this.WhereClause = predicate;
            return this;
        }

        public SoqlQuery Where(string format, params object[] args) => 
            this.Where(string.Format(format, args));

        public string[] SelectColumns { get; private set; }

        public string[] SelectColumnAliases { get; private set; }

        public string WhereClause { get; private set; }

        public SoqlOrderDirection OrderDirection { get; private set; }

        public string[] OrderByColumns { get; private set; }

        public string[] GroupByColumns { get; private set; }

        public int LimitValue { get; private set; }

        public int OffsetValue { get; private set; }

        public string SearchText { get; private set; }

        [Serializable, CompilerGenerated]
        private sealed class <>c
        {
            public static readonly SoqlQuery.<>c <>9 = new SoqlQuery.<>c();
            public static Func<string, string, string> <>9__49_0;
            public static Func<string, string> <>9__51_0;
            public static Func<string, bool> <>9__61_0;
            public static Func<string, bool> <>9__61_1;

            internal string <As>b__51_0(string a) => 
                a.ToLower();

            internal bool <getNonEmptyValues>b__61_0(string s) => 
                !string.IsNullOrEmpty(s);

            internal bool <getNonEmptyValues>b__61_1(string s) => 
                !string.IsNullOrEmpty(s);

            internal string <ToString>b__49_0(string c, string a) => 
                $"{c} AS {a}";
        }
    }
}

