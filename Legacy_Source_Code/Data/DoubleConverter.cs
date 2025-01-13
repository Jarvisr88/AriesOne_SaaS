namespace DMEWorks.Data
{
    using System;
    using System.Globalization;
    using System.Runtime.InteropServices;

    internal class DoubleConverter : Converter<double>
    {
        public override string ToString(double value) => 
            value.ToString(CultureInfo.InvariantCulture);

        public override bool TryParse(string value, out double result) => 
            double.TryParse(value, NumberStyles.Any, CultureInfo.InvariantCulture, out result);
    }
}

