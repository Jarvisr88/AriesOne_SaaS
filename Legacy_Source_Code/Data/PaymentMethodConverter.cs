namespace DMEWorks.Data
{
    using System;
    using System.Runtime.InteropServices;

    public class PaymentMethodConverter : Converter<PaymentMethod>
    {
        public const string Cash = "Cash";
        public const string Check = "Check";
        public const string CreditCard = "Credit Card";

        public override string ToString(PaymentMethod value)
        {
            switch (value)
            {
                case PaymentMethod.Cash:
                    return "Cash";

                case PaymentMethod.Check:
                    return "Check";

                case PaymentMethod.CreditCard:
                    return "Credit Card";
            }
            return "";
        }

        public override bool TryParse(string value, out PaymentMethod result)
        {
            if ("Cash".Equals(value, StringComparison.OrdinalIgnoreCase))
            {
                result = PaymentMethod.Cash;
            }
            else if ("Check".Equals(value, StringComparison.OrdinalIgnoreCase))
            {
                result = PaymentMethod.Check;
            }
            else
            {
                if (!"Credit Card".Equals(value, StringComparison.OrdinalIgnoreCase))
                {
                    result = PaymentMethod.Cash;
                    return false;
                }
                result = PaymentMethod.CreditCard;
            }
            return true;
        }
    }
}

