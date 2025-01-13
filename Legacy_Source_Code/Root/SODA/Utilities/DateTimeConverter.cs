namespace SODA.Utilities
{
    using System;

    public class DateTimeConverter
    {
        public static readonly DateTime UnixEpoch = new DateTime(0x7b2, 1, 1, 0, 0, 0, DateTimeKind.Utc);

        public static DateTime FromUnixTimestamp(double unixTimestamp) => 
            UnixEpoch.AddSeconds(unixTimestamp).ToLocalTime();
    }
}

