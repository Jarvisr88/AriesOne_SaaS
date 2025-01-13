namespace DMEWorks.Data
{
    using System;
    using System.Runtime.InteropServices;

    public abstract class Converter<T> where T: struct
    {
        private static Converter<T> _DefaultConverter;

        protected Converter()
        {
        }

        private static Converter<T> CreateConverter()
        {
            Type type = typeof(T);
            if (type == typeof(DateTime))
            {
                return (Converter<T>) new DateTimeConverter();
            }
            if (type == typeof(decimal))
            {
                return (Converter<T>) new DecimalConverter();
            }
            if (type == typeof(double))
            {
                return (Converter<T>) new DoubleConverter();
            }
            if (type == typeof(Guid))
            {
                return (Converter<T>) new GuidConverter();
            }
            if (type == typeof(PaymentMethod))
            {
                return (Converter<T>) new PaymentMethodConverter();
            }
            if (type != typeof(VoidMethod))
            {
                throw new NotImplementedException("");
            }
            return (Converter<T>) new VoidMethodConverter();
        }

        public T? Parse(string text)
        {
            T local;
            if (this.TryParse(text, out local))
            {
                return new T?(local);
            }
            return null;
        }

        public abstract string ToString(T value);
        public virtual string ToString(T? value) => 
            (value != null) ? this.ToString(value.Value) : string.Empty;

        public abstract bool TryParse(string text, out T result);

        public static Converter<T> Default
        {
            get
            {
                Converter<T> converter = Converter<T>._DefaultConverter;
                if (converter == null)
                {
                    converter = Converter<T>.CreateConverter();
                    Converter<T>._DefaultConverter = converter;
                }
                return converter;
            }
        }
    }
}

