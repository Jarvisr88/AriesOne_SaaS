namespace DMEWorks
{
    using System;
    using System.Text;

    public class DmercHelper
    {
        public const string DMERC_0102A = "DMERC 01.02A";
        public const string DMERC_0102B = "DMERC 01.02B";
        public const string DMERC_0203A = "DMERC 02.03A";
        public const string DMERC_0203B = "DMERC 02.03B";
        public const string DMERC_0302 = "DMERC 03.02";
        public const string DMERC_0403B = "DMERC 04.03B";
        public const string DMERC_0403C = "DMERC 04.03C";
        public const string DMERC_0602B = "DMERC 06.02B";
        public const string DMERC_0702A = "DMERC 07.02A";
        public const string DMERC_0702B = "DMERC 07.02B";
        public const string DMERC_0802 = "DMERC 08.02";
        public const string DMERC_0902 = "DMERC 09.02";
        public const string DMERC_1002A = "DMERC 10.02A";
        public const string DMERC_1002B = "DMERC 10.02B";
        public const string DMERC_4842 = "DMERC 484.2";
        public const string DMERC_DRORDER = "DMERC DRORDER";
        public const string DMERC_URO = "DMERC URO";
        public const string DME_0404B = "DME 04.04B";
        public const string DME_0404C = "DME 04.04C";
        public const string DME_0603B = "DME 06.03B";
        public const string DME_0703A = "DME 07.03A";
        public const string DME_0903 = "DME 09.03";
        public const string DME_1003 = "DME 10.03";
        public const string DME_48403 = "DME 484.03";
        public const DmercType Undefined = ((DmercType) 0);

        public static string Dmerc2String(DmercType value)
        {
            switch (value)
            {
                case DmercType.DMERC_0102A:
                    return "DMERC 01.02A";

                case DmercType.DMERC_0102B:
                    return "DMERC 01.02B";

                case DmercType.DMERC_0203A:
                    return "DMERC 02.03A";

                case DmercType.DMERC_0203B:
                    return "DMERC 02.03B";

                case DmercType.DMERC_0302:
                    return "DMERC 03.02";

                case DmercType.DMERC_0403B:
                    return "DMERC 04.03B";

                case DmercType.DMERC_0403C:
                    return "DMERC 04.03C";

                case DmercType.DMERC_0602B:
                    return "DMERC 06.02B";

                case DmercType.DMERC_0702A:
                    return "DMERC 07.02A";

                case DmercType.DMERC_0702B:
                    return "DMERC 07.02B";

                case DmercType.DMERC_0802:
                    return "DMERC 08.02";

                case DmercType.DMERC_0902:
                    return "DMERC 09.02";

                case DmercType.DMERC_1002A:
                    return "DMERC 10.02A";

                case DmercType.DMERC_1002B:
                    return "DMERC 10.02B";

                case DmercType.DMERC_4842:
                    return "DMERC 484.2";

                case DmercType.DMERC_DRORDER:
                    return "DMERC DRORDER";

                case DmercType.DMERC_URO:
                    return "DMERC URO";

                case DmercType.DME_0404B:
                    return "DME 04.04B";

                case DmercType.DME_0404C:
                    return "DME 04.04C";

                case DmercType.DME_0603B:
                    return "DME 06.03B";

                case DmercType.DME_0703A:
                    return "DME 07.03A";

                case DmercType.DME_0903:
                    return "DME 09.03";

                case DmercType.DME_1003:
                    return "DME 10.03";

                case DmercType.DME_48403:
                    return "DME 484.03";
            }
            return "";
        }

        public static string GetDescription(DmercType value)
        {
            if (value == ((DmercType) 0))
            {
                return "";
            }
            StringBuilder builder = new StringBuilder(0x40);
            builder.Append("(").Append(GetVersion(value)).Append(")  ").Append(GetName(value));
            string status = GetStatus(value);
            if (!string.IsNullOrEmpty(status))
            {
                builder.Append(" - ").Append(status);
            }
            return builder.ToString();
        }

        public static string GetName(DmercType value)
        {
            switch (value)
            {
                case DmercType.DMERC_0102A:
                    return "HOSPITAL BEDS";

                case DmercType.DMERC_0102B:
                    return "SUPPORT SURFACES";

                case DmercType.DMERC_0203A:
                    return "MOTORIZED WHEELCHAIRS";

                case DmercType.DMERC_0203B:
                    return "MANUAL WHEELCHAIRS";

                case DmercType.DMERC_0302:
                    return "CONTINUOUS POSITIVE AIRWAY PRESSURE (CPAP)";

                case DmercType.DMERC_0403B:
                    return "LYMPHEDEMA PUMPS";

                case DmercType.DMERC_0403C:
                    return "OSTEOGENESIS STIMULATORS";

                case DmercType.DMERC_0602B:
                    return "TRANSCUTANEOUS ELECTRICAL NERVE STIMULATOR (TENS)";

                case DmercType.DMERC_0702A:
                    return "SEAT LIFT MECHANISM";

                case DmercType.DMERC_0702B:
                    return "POWER OPERATED VEHICLE (POV)";

                case DmercType.DMERC_0802:
                    return "SUPPORT SURFACES";

                case DmercType.DMERC_0902:
                    return "EXTERNAL INFUSION PUMP";

                case DmercType.DMERC_1002A:
                    return "PARENTERAL NUTRITION";

                case DmercType.DMERC_1002B:
                    return "ENTERAL NUTRITION";

                case DmercType.DMERC_4842:
                    return "OXYGEN";

                case DmercType.DMERC_DRORDER:
                    return "PHYSICIAN'S ORDER";

                case DmercType.DMERC_URO:
                    return "UROLOGICAL CERTIFICATION";

                case DmercType.DME_0404B:
                    return "PNEUMATIC COMPRESSION DEVICES";

                case DmercType.DME_0404C:
                    return "OSTEOGENESIS STIMULATORS";

                case DmercType.DME_0603B:
                    return "TRANSCUTANEOUS ELECTRICAL NERVE STIMULATOR (TENS)";

                case DmercType.DME_0703A:
                    return "SEAT LIFT MECHANISMS";

                case DmercType.DME_0903:
                    return "EXTERNAL INFUSION PUMPS";

                case DmercType.DME_1003:
                    return "ENTERAL AND PARENTERAL NUTRITION";

                case DmercType.DME_48403:
                    return "OXYGEN";
            }
            return "";
        }

        public static string GetStatus(DmercType value)
        {
            switch (value)
            {
                case DmercType.DMERC_0102A:
                    return "eliminated";

                case DmercType.DMERC_0102B:
                    return "eliminated";

                case DmercType.DMERC_0203A:
                    return "obsolete";

                case DmercType.DMERC_0203B:
                    return "obsolete";

                case DmercType.DMERC_0302:
                    return "obsolete";

                case DmercType.DMERC_0403B:
                    return "obsolete";

                case DmercType.DMERC_0403C:
                    return "obsolete";

                case DmercType.DMERC_0602B:
                    return "obsolete";

                case DmercType.DMERC_0702A:
                    return "obsolete";

                case DmercType.DMERC_0702B:
                    return "";

                case DmercType.DMERC_0802:
                    return "";

                case DmercType.DMERC_0902:
                    return "obsolete";

                case DmercType.DMERC_1002A:
                    return "obsolete";

                case DmercType.DMERC_1002B:
                    return "obsolete";

                case DmercType.DMERC_4842:
                    return "obsolete";

                case DmercType.DMERC_DRORDER:
                    return "";

                case DmercType.DMERC_URO:
                    return "";

                case DmercType.DME_0404B:
                    return "";

                case DmercType.DME_0404C:
                    return "";

                case DmercType.DME_0603B:
                    return "";

                case DmercType.DME_0703A:
                    return "";

                case DmercType.DME_0903:
                    return "";

                case DmercType.DME_1003:
                    return "";

                case DmercType.DME_48403:
                    return "";
            }
            return "";
        }

        public static string GetTableName(DmercType value)
        {
            switch (value)
            {
                case DmercType.DMERC_0102A:
                    return "tbl_cmnform_0102a";

                case DmercType.DMERC_0102B:
                    return "tbl_cmnform_0102b";

                case DmercType.DMERC_0203A:
                    return "tbl_cmnform_0203a";

                case DmercType.DMERC_0203B:
                    return "tbl_cmnform_0203b";

                case DmercType.DMERC_0302:
                    return "tbl_cmnform_0302";

                case DmercType.DMERC_0403B:
                    return "tbl_cmnform_0403b";

                case DmercType.DMERC_0403C:
                    return "tbl_cmnform_0403c";

                case DmercType.DMERC_0602B:
                    return "tbl_cmnform_0602b";

                case DmercType.DMERC_0702A:
                    return "tbl_cmnform_0702a";

                case DmercType.DMERC_0702B:
                    return "tbl_cmnform_0702b";

                case DmercType.DMERC_0802:
                    return "tbl_cmnform_0802";

                case DmercType.DMERC_0902:
                    return "tbl_cmnform_0902";

                case DmercType.DMERC_1002A:
                    return "tbl_cmnform_1002a";

                case DmercType.DMERC_1002B:
                    return "tbl_cmnform_1002b";

                case DmercType.DMERC_4842:
                    return "tbl_cmnform_4842";

                case DmercType.DMERC_DRORDER:
                    return "tbl_cmnform_drorder";

                case DmercType.DMERC_URO:
                    return "tbl_cmnform_uro";

                case DmercType.DME_0404B:
                    return "tbl_cmnform_0404b";

                case DmercType.DME_0404C:
                    return "tbl_cmnform_0404c";

                case DmercType.DME_0603B:
                    return "tbl_cmnform_0603b";

                case DmercType.DME_0703A:
                    return "tbl_cmnform_0703a";

                case DmercType.DME_0903:
                    return "tbl_cmnform_0903";

                case DmercType.DME_1003:
                    return "tbl_cmnform_1003";

                case DmercType.DME_48403:
                    return "tbl_cmnform_48403";
            }
            return "";
        }

        public static string GetVersion(DmercType value)
        {
            switch (value)
            {
                case DmercType.DMERC_0102A:
                    return "01.02A";

                case DmercType.DMERC_0102B:
                    return "01.02B";

                case DmercType.DMERC_0203A:
                    return "02.03A";

                case DmercType.DMERC_0203B:
                    return "02.03B";

                case DmercType.DMERC_0302:
                    return "03.02";

                case DmercType.DMERC_0403B:
                    return "04.03B";

                case DmercType.DMERC_0403C:
                    return "04.03C";

                case DmercType.DMERC_0602B:
                    return "06.02B";

                case DmercType.DMERC_0702A:
                    return "07.02A";

                case DmercType.DMERC_0702B:
                    return "07.02B";

                case DmercType.DMERC_0802:
                    return "08.02";

                case DmercType.DMERC_0902:
                    return "09.02";

                case DmercType.DMERC_1002A:
                    return "10.02A";

                case DmercType.DMERC_1002B:
                    return "10.02B";

                case DmercType.DMERC_4842:
                    return "484.2";

                case DmercType.DMERC_DRORDER:
                    return "DRORDER";

                case DmercType.DMERC_URO:
                    return "URO";

                case DmercType.DME_0404B:
                    return "04.04B";

                case DmercType.DME_0404C:
                    return "04.04C";

                case DmercType.DME_0603B:
                    return "06.03B";

                case DmercType.DME_0703A:
                    return "07.03A";

                case DmercType.DME_0903:
                    return "09.03";

                case DmercType.DME_1003:
                    return "10.03";

                case DmercType.DME_48403:
                    return "484.03";
            }
            return "";
        }

        public static DmercType String2Dmerc(string value) => 
            (string.Compare(value, "DMERC 01.02A", true) != 0) ? ((string.Compare(value, "DMERC 01.02B", true) != 0) ? ((string.Compare(value, "DMERC 02.03A", true) != 0) ? ((string.Compare(value, "DMERC 02.03B", true) != 0) ? ((string.Compare(value, "DMERC 03.02", true) != 0) ? ((string.Compare(value, "DMERC 04.03B", true) != 0) ? ((string.Compare(value, "DMERC 04.03C", true) != 0) ? ((string.Compare(value, "DMERC 06.02B", true) != 0) ? ((string.Compare(value, "DMERC 07.02A", true) != 0) ? ((string.Compare(value, "DMERC 07.02B", true) != 0) ? ((string.Compare(value, "DMERC 08.02", true) != 0) ? ((string.Compare(value, "DMERC 09.02", true) != 0) ? ((string.Compare(value, "DMERC 10.02A", true) != 0) ? ((string.Compare(value, "DMERC 10.02B", true) != 0) ? ((string.Compare(value, "DMERC 484.2", true) != 0) ? ((string.Compare(value, "DMERC DRORDER", true) != 0) ? ((string.Compare(value, "DMERC URO", true) != 0) ? ((string.Compare(value, "DME 04.04B", true) != 0) ? ((string.Compare(value, "DME 04.04C", true) != 0) ? ((string.Compare(value, "DME 06.03B", true) != 0) ? ((string.Compare(value, "DME 07.03A", true) != 0) ? ((string.Compare(value, "DME 09.03", true) != 0) ? ((string.Compare(value, "DME 10.03", true) != 0) ? ((string.Compare(value, "DME 484.03", true) != 0) ? ((DmercType) 0) : DmercType.DME_48403) : DmercType.DME_1003) : DmercType.DME_0903) : DmercType.DME_0703A) : DmercType.DME_0603B) : DmercType.DME_0404C) : DmercType.DME_0404B) : DmercType.DMERC_URO) : DmercType.DMERC_DRORDER) : DmercType.DMERC_4842) : DmercType.DMERC_1002B) : DmercType.DMERC_1002A) : DmercType.DMERC_0902) : DmercType.DMERC_0802) : DmercType.DMERC_0702B) : DmercType.DMERC_0702A) : DmercType.DMERC_0602B) : DmercType.DMERC_0403C) : DmercType.DMERC_0403B) : DmercType.DMERC_0302) : DmercType.DMERC_0203B) : DmercType.DMERC_0203A) : DmercType.DMERC_0102B) : DmercType.DMERC_0102A;
    }
}

