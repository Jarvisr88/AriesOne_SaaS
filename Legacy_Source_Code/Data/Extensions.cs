namespace DMEWorks.Data
{
    using DMEWorks.Data.Serialization;
    using System;
    using System.Runtime.CompilerServices;

    internal static class Extensions
    {
        public static void Append<T>(this Pairs pairs, Enum name, T? value) where T: struct
        {
            if (value != null)
            {
                Pair item = new Pair();
                item.Name = name.ToString();
                item.Value = Converter<T>.Default.ToString(value.Value);
                pairs.Elements.Add(item);
            }
        }

        public static void Append(this Pairs pairs, Enum name, string value)
        {
            if (value != null)
            {
                value = value.Trim();
                if (value.Length != 0)
                {
                    Pair item = new Pair();
                    item.Name = name.ToString();
                    item.Value = value;
                    pairs.Elements.Add(item);
                }
            }
        }

        public static void PutInto<T>(this string value, ref T? field) where T: struct
        {
            T local;
            if (Converter<T>.Default.TryParse(value, out local))
            {
                field = new T?(local);
            }
            else
            {
                field = 0;
            }
        }

        public static void PutInto(this string value, ref string field)
        {
            field = (value != null) ? value : string.Empty;
        }
    }
}

