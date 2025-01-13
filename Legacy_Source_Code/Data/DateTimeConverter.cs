namespace DMEWorks.Data
{
    using System;
    using System.Globalization;
    using System.Runtime.InteropServices;

    internal class DateTimeConverter : Converter<DateTime>
    {
        public override string ToString(DateTime value) => 
            value.ToString("d", CultureInfo.InvariantCulture);

        public override bool TryParse(string value, out DateTime result) => 
            DateTime.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.AllowTrailingWhite | DateTimeStyles.AllowLeadingWhite, out result);
    }
}

