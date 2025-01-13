namespace DMEWorks.Serials
{
    using System;
    using System.Runtime.InteropServices;

    [StructLayout(LayoutKind.Sequential)]
    public struct SerialData
    {
        private readonly BigNumber Data;
        public const string Username = "DMEUser";
        public const string Password = "DMEPassword";
        private SerialData(BigNumber data)
        {
            this.Data = data;
            if ((((byte) ((((((((((((((((this.Data.Byte00 ^ this.Data.Byte01) ^ this.Data.Byte02) ^ this.Data.Byte03) ^ this.Data.Byte04) ^ this.Data.Byte05) ^ this.Data.Byte06) ^ this.Data.Byte07) ^ this.Data.Byte08) ^ this.Data.Byte09) ^ this.Data.Byte10) ^ this.Data.Byte11) ^ this.Data.Byte12) ^ this.Data.Byte13) ^ this.Data.Byte14) ^ this.Data.Byte15) ^ this.Data.Byte16)) != 0) || (this.Data.Byte16 != 0))
            {
                throw new ArgumentException("Serial is not valid", "data");
            }
        }

        public SerialData(string s) : this(new BigNumber(s))
        {
        }

        public byte MaxCount() => 
            this.Data.Byte00;

        public DateTime ExpirationDate() => 
            !(((this.Data.Byte04 == 0) & (this.Data.Byte05 == 0)) & (this.Data.Byte06 == 0)) ? new DateTime(0xc92a69c000L * Math.Min(this.Data.Byte04 + (0x100 * (this.Data.Byte05 + (0x100 * this.Data.Byte06))), 0x37b9da)) : DateTime.MaxValue;

        public int ClientNumber() => 
            this.Data.Byte07 + (0x100 * this.Data.Byte08);

        public bool IsDemoSerial() => 
            this.Data.IsZero;

        public bool IsExpired() => 
            !this.Data.IsZero && (this.ExpirationDate() < DateTime.Now);

        public override string ToString() => 
            this.Data.ToString();

        public string ToString(string format) => 
            this.Data.ToString(format, null);

        public string ToString(string format, IFormatProvider provider) => 
            this.Data.ToString(format, provider);
    }
}

