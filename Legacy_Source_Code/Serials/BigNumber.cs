namespace DMEWorks.Serials
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;
    using System.Text;

    [StructLayout(LayoutKind.Sequential)]
    public struct BigNumber
    {
        private const byte MaxSize = 0x11;
        public byte Byte00 { get; }
        public byte Byte01 { get; }
        public byte Byte02 { get; }
        public byte Byte03 { get; }
        public byte Byte04 { get; }
        public byte Byte05 { get; }
        public byte Byte06 { get; }
        public byte Byte07 { get; }
        public byte Byte08 { get; }
        public byte Byte09 { get; }
        public byte Byte10 { get; }
        public byte Byte11 { get; }
        public byte Byte12 { get; }
        public byte Byte13 { get; }
        public byte Byte14 { get; }
        public byte Byte15 { get; }
        public byte Byte16 { get; }
        private BigNumber(byte[] value)
        {
            if (value == null)
            {
                throw new ArgumentNullException("value");
            }
            if (value.Length != 0x11)
            {
                throw new ArgumentException("array length must be 17", "value");
            }
            this.<Byte00>k__BackingField = value[0];
            this.<Byte01>k__BackingField = value[1];
            this.<Byte02>k__BackingField = value[2];
            this.<Byte03>k__BackingField = value[3];
            this.<Byte04>k__BackingField = value[4];
            this.<Byte05>k__BackingField = value[5];
            this.<Byte06>k__BackingField = value[6];
            this.<Byte07>k__BackingField = value[7];
            this.<Byte08>k__BackingField = value[8];
            this.<Byte09>k__BackingField = value[9];
            this.<Byte10>k__BackingField = value[10];
            this.<Byte11>k__BackingField = value[11];
            this.<Byte12>k__BackingField = value[12];
            this.<Byte13>k__BackingField = value[13];
            this.<Byte14>k__BackingField = value[14];
            this.<Byte15>k__BackingField = value[15];
            this.<Byte16>k__BackingField = value[0x10];
        }

        private static char? Byte2Char(byte value)
        {
            if (value <= 9)
            {
                return new char?((char) ((ushort) (0x30 + value)));
            }
            if (value <= 0x23)
            {
                return new char?((char) ((ushort) (0x41 + (value - 10))));
            }
            return null;
        }

        private static byte? Char2Byte(char value)
        {
            if (('0' <= value) && (value <= '9'))
            {
                return new byte?((byte) (value - '0'));
            }
            if (('a' <= value) && (value <= 'z'))
            {
                return new byte?((byte) ((value - 'a') + 10));
            }
            if (('A' <= value) && (value <= 'Z'))
            {
                return new byte?((byte) ((value - 'A') + 10));
            }
            return null;
        }

        public BigNumber(string value)
        {
            if (value == null)
            {
                throw new ArgumentNullException("value");
            }
            this = Parse(value);
        }

        public static BigNumber Parse(string s)
        {
            if (s == null)
            {
                throw new ArgumentNullException("s");
            }
            byte[] buffer = new byte[0x11];
            for (int i = s.Length - 1; 0 <= i; i--)
            {
                byte? nullable = Char2Byte(s[i]);
                if (nullable != null)
                {
                    int num2 = nullable.Value;
                    for (int j = 0; j < 0x11; j++)
                    {
                        num2 += 0x24 * buffer[j];
                        buffer[j] = (byte) (num2 % 0x100);
                        num2 /= 0x100;
                    }
                }
            }
            return new BigNumber(buffer);
        }

        public override string ToString() => 
            this.ToString("N", null);

        public string ToString(string format) => 
            this.ToString(format, null);

        public string ToString(string format, IFormatProvider provider)
        {
            if ((format == null) || (format.Length == 0))
            {
                format = "D";
            }
            if (format.Length != 1)
            {
                throw new FormatException("Invalid Format Specification");
            }
            bool flag = (format[0] == 'd') || (format[0] == 'D');
            byte[] buffer1 = new byte[0x11];
            buffer1[0] = this.Byte00;
            buffer1[1] = this.Byte01;
            buffer1[2] = this.Byte02;
            buffer1[3] = this.Byte03;
            buffer1[4] = this.Byte04;
            buffer1[5] = this.Byte05;
            buffer1[6] = this.Byte06;
            buffer1[7] = this.Byte07;
            buffer1[8] = this.Byte08;
            buffer1[9] = this.Byte09;
            buffer1[10] = this.Byte10;
            buffer1[11] = this.Byte11;
            buffer1[12] = this.Byte12;
            buffer1[13] = this.Byte13;
            buffer1[14] = this.Byte14;
            buffer1[15] = this.Byte15;
            buffer1[0x10] = this.Byte16;
            byte[] buffer = buffer1;
            StringBuilder builder = new StringBuilder(30);
            int num = 0;
            while (num <= 0x18)
            {
                int num2 = 0;
                int index = buffer.Length - 1;
                while (true)
                {
                    if (0 > index)
                    {
                        if (flag && ((builder.Length % 6) == 5))
                        {
                            builder.Append('-');
                        }
                        builder.Append(Byte2Char((byte) num2).Value);
                        num++;
                        break;
                    }
                    num2 = (0x100 * num2) + buffer[index];
                    buffer[index] = (byte) (num2 / 0x24);
                    num2 = num2 % 0x24;
                    index--;
                }
            }
            return builder.ToString();
        }

        public bool IsZero =>
            ((((this.Byte00 | this.Byte01) | this.Byte02) | this.Byte03) == 0) && (((((this.Byte04 | this.Byte05) | this.Byte06) | this.Byte07) == 0) && (((((this.Byte08 | this.Byte09) | this.Byte10) | this.Byte11) == 0) && (((((this.Byte12 | this.Byte13) | this.Byte14) | this.Byte15) == 0) && (this.Byte16 == 0))));
    }
}

