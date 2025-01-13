namespace DMEWorks.Core
{
    using System;
    using System.Collections.Generic;
    using System.Reflection;
    using System.Runtime.InteropServices;

    public class FormParameters
    {
        private readonly Dictionary<string, object> _storage;
        private bool _readonly;

        public FormParameters()
        {
            this._storage = new Dictionary<string, object>(StringComparer.InvariantCultureIgnoreCase);
        }

        public FormParameters(string query) : this()
        {
            if (!string.IsNullOrEmpty(query))
            {
                int num = 0;
                int length = query.Length;
                while (num < length)
                {
                    int startIndex = num;
                    int num4 = -1;
                    while (true)
                    {
                        if (num < length)
                        {
                            char ch = query[num];
                            if (ch != '&')
                            {
                                if ((ch == '=') && (num4 < 0))
                                {
                                    num4 = num;
                                }
                                num++;
                                continue;
                            }
                        }
                        string str = null;
                        string str2 = null;
                        if (0 > num4)
                        {
                            str2 = query.Substring(startIndex, num - startIndex);
                        }
                        else
                        {
                            str = query.Substring(startIndex, num4 - startIndex);
                            str2 = query.Substring(num4 + 1, (num - num4) - 1);
                        }
                        this[str] = str2;
                        if ((num == (length - 1)) && (query[num] == '&'))
                        {
                            this[""] = "";
                        }
                        num++;
                        break;
                    }
                }
            }
        }

        public FormParameters(string key, object value) : this()
        {
            this._storage[key] = value;
            this._readonly = true;
        }

        public void Clear()
        {
            if (this._readonly)
            {
                throw new InvalidOperationException("Cannot change readonly object");
            }
            this._storage.Clear();
        }

        public bool ContainsKey(string key) => 
            this._storage.ContainsKey(key);

        public void SetReadonly()
        {
            this._readonly = true;
        }

        public bool TryGetValue(string key, out bool value)
        {
            object obj2;
            if (this._storage.TryGetValue(key, out obj2))
            {
                bool? nullable = NullableConvert.ToBoolean(obj2);
                if (nullable != null)
                {
                    value = nullable.Value;
                    return true;
                }
            }
            value = false;
            return false;
        }

        public bool TryGetValue(string key, out DateTime value)
        {
            object obj2;
            if (this._storage.TryGetValue(key, out obj2))
            {
                DateTime? nullable = NullableConvert.ToDateTime(obj2);
                if (nullable != null)
                {
                    value = nullable.Value;
                    return true;
                }
            }
            value = DateTime.MinValue;
            return false;
        }

        public bool TryGetValue(string key, out double value)
        {
            object obj2;
            if (this._storage.TryGetValue(key, out obj2))
            {
                double? nullable = NullableConvert.ToDouble(obj2);
                if (nullable != null)
                {
                    value = nullable.Value;
                    return true;
                }
            }
            value = 0.0;
            return false;
        }

        public bool TryGetValue(string key, out int value)
        {
            object obj2;
            if (this._storage.TryGetValue(key, out obj2))
            {
                int? nullable = NullableConvert.ToInt32(obj2);
                if (nullable != null)
                {
                    value = nullable.Value;
                    return true;
                }
            }
            value = 0;
            return false;
        }

        public bool TryGetValue(string key, out object value) => 
            this._storage.TryGetValue(key, out value);

        public bool TryGetValue(string key, out string value)
        {
            object obj2;
            if (this._storage.TryGetValue(key, out obj2))
            {
                value = NullableConvert.ToString(obj2);
                return true;
            }
            value = null;
            return false;
        }

        public object this[string key]
        {
            get
            {
                object obj2;
                return (!this._storage.TryGetValue(key, out obj2) ? null : obj2);
            }
            set
            {
                if (this._readonly)
                {
                    throw new InvalidOperationException("Cannot change readonly object");
                }
                this._storage[key] = value;
            }
        }

        public int Count =>
            this._storage.Count;
    }
}

