namespace DMEWorks.Data.MySql
{
    using DMEWorks.Expressions;
    using System;
    using System.Collections.Generic;
    using System.Runtime.CompilerServices;
    using System.Text;

    public static class MySqlFilterUtilities
    {
        private const char quote = '\'';
        private const char percent = '%';

        public static string BuildFilter(IEnumerable<QueryExpression> expressions, string searchString)
        {
            if (expressions == null)
            {
                throw new ArgumentNullException("expressions");
            }
            if (searchString == null)
            {
                throw new ArgumentNullException("searchString");
            }
            return QueryExpressionVisitor.ExpressionToString(Utilities.BuildFilter(expressions, searchString));
        }

        public static string BuildQuotedContainsPattern(this string value) => 
            QuoteLikeString(value, StringFilterType.Contains);

        private static string QuoteLikeString(string value, StringFilterType type)
        {
            int num = (value != null) ? value.Length : 0;
            StringBuilder builder = new StringBuilder((2 + (3 * num)) + 2);
            builder.Append('\'');
            if ((type == StringFilterType.Contains) || (type == StringFilterType.EndWith))
            {
                builder.Append('%');
            }
            int num2 = 0;
            goto TR_001A;
        TR_0003:
            num2++;
        TR_001A:
            while (true)
            {
                if (num2 >= num)
                {
                    if ((type == StringFilterType.Contains) || (type == StringFilterType.StartWith))
                    {
                        builder.Append('%');
                    }
                    builder.Append('\'');
                    return builder.ToString();
                }
                char ch = value[num2];
                if (ch > '"')
                {
                    if (ch <= '\'')
                    {
                        if (ch == '%')
                        {
                            builder.Append('\'').Append('%');
                            break;
                        }
                        if (ch == '\'')
                        {
                            builder.Append('\'').Append('\'');
                            break;
                        }
                    }
                    else
                    {
                        if (ch == '\\')
                        {
                            builder.Append('\'').Append('\\');
                            break;
                        }
                        if (ch == '_')
                        {
                            builder.Append('\'').Append('_');
                            break;
                        }
                    }
                }
                else
                {
                    if (ch == '\0')
                    {
                        builder.Append('\'').Append('0');
                        break;
                    }
                    switch (ch)
                    {
                        case '\b':
                            builder.Append('\'').Append('b');
                            goto TR_0003;

                        case '\t':
                            builder.Append('\'').Append('t');
                            goto TR_0003;

                        case '\n':
                            builder.Append('\'').Append('n');
                            goto TR_0003;

                        case '\v':
                        case '\f':
                            break;

                        case '\r':
                            builder.Append('\'').Append('r');
                            goto TR_0003;

                        default:
                            if (ch != '"')
                            {
                                break;
                            }
                            builder.Append('\'').Append('"');
                            goto TR_0003;
                    }
                }
                builder.Append(ch);
                break;
            }
            goto TR_0003;
        }

        private enum StringFilterType
        {
            StartWith,
            EndWith,
            Contains
        }
    }
}

