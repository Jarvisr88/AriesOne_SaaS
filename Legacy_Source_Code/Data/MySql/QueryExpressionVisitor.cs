namespace DMEWorks.Data.MySql
{
    using DMEWorks.Expressions;
    using System;
    using System.Globalization;
    using System.Linq.Expressions;
    using System.Text;

    internal sealed class QueryExpressionVisitor : DmeworksExpressionVisitor
    {
        private readonly StringBuilder m_out = new StringBuilder();

        private QueryExpressionVisitor()
        {
        }

        internal static string ExpressionToString(Expression node)
        {
            QueryExpressionVisitor visitor1 = new QueryExpressionVisitor();
            visitor1.Visit(node);
            return visitor1.ToString();
        }

        private void Out(char c)
        {
            this.m_out.Append(c);
        }

        private void Out(string s)
        {
            this.m_out.Append(s);
        }

        public override string ToString() => 
            this.m_out.ToString();

        protected override Expression VisitBinary(BinaryExpression node)
        {
            string str;
            ExpressionType nodeType = node.NodeType;
            if ((nodeType - 2) <= ExpressionType.AddChecked)
            {
                str = "AND";
            }
            else
            {
                if ((nodeType - ExpressionType.Or) > ExpressionType.AddChecked)
                {
                    throw new NotSupportedException();
                }
                str = "OR";
            }
            this.Out('(');
            this.Visit(node.Left);
            this.Out(' ');
            this.Out(str);
            this.Out(' ');
            this.Visit(node.Right);
            this.Out(')');
            return node;
        }

        protected override Expression VisitLambda<TDelegate>(Expression<TDelegate> node)
        {
            throw new NotSupportedException();
        }

        protected override Expression VisitPrimitive(PrimitiveExpression node)
        {
            QueryExpression expression = node as QueryExpression;
            if (expression == null)
            {
                throw new NotSupportedException();
            }
            this.Out(expression.ExpressionText);
            return node;
        }

        protected override Expression VisitPrimitiveComparison(PrimitiveComparisonExpression node)
        {
            switch (node.PrimitiveType)
            {
                case PrimitiveType.Date:
                {
                    DateTime time = (DateTime) node.Value;
                    this.Out('(');
                    this.Out(time.ToString(@"\'yyyy-MM-dd\'", CultureInfo.InvariantCulture));
                    this.Out(" <= ");
                    this.Visit(node.Expression);
                    this.Out(" AND ");
                    this.Visit(node.Expression);
                    this.Out(" < ");
                    this.Out(time.AddDays(1.0).ToString(@"\'yyyy-MM-dd\'", CultureInfo.InvariantCulture));
                    this.Out(')');
                    break;
                }
                case PrimitiveType.Decimal:
                case PrimitiveType.Float:
                case PrimitiveType.Int:
                    this.Visit(node.Expression);
                    this.Out(" = ");
                    this.Out(Convert.ToString(node.Value, CultureInfo.InvariantCulture));
                    break;

                case PrimitiveType.String:
                    this.Visit(node.Expression);
                    this.Out(" LIKE ");
                    this.Out(((string) node.Value).BuildQuotedContainsPattern());
                    break;

                default:
                    throw new NotSupportedException();
            }
            return node;
        }
    }
}

