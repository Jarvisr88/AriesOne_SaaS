namespace DMEWorks.Data
{
    using System;
    using System.Globalization;
    using System.Runtime.InteropServices;

    internal class GuidConverter : Converter<Guid>
    {
        public override string ToString(Guid value) => 
            value.ToString("D", CultureInfo.InvariantCulture);

        public override bool TryParse(string value, out Guid result) => 
            Guid.TryParseExact(value, "D", out result);
    }
}

