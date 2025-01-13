namespace DMEWorks.Data
{
    using System;
    using System.Globalization;
    using System.Runtime.InteropServices;

    internal class DecimalConverter : Converter<decimal>
    {
        public override string ToString(decimal value) => 
            value.ToString(CultureInfo.InvariantCulture);

        public override bool TryParse(string value, out decimal result) => 
            decimal.TryParse(value, NumberStyles.Any, CultureInfo.InvariantCulture, out result);
    }
}

