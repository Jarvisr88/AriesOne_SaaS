namespace DMEWorks.Csv
{
    using DMEWorks.Csv.Resources;
    using System;
    using System.Collections;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Data;
    using System.Globalization;
    using System.IO;
    using System.Reflection;

    public class CachedCsvReader : CsvReader, IListSource
    {
        private List<string[]> _records;
        private long _currentRecordIndex;
        private bool _readingStream;
        private CsvBindingList _bindingList;

        public CachedCsvReader(TextReader reader, bool hasHeaders) : this(reader, hasHeaders, 0x1000)
        {
        }

        public CachedCsvReader(TextReader reader, bool hasHeaders, char delimiter) : this(reader, hasHeaders, delimiter, '"', '"', '#', true, 0x1000)
        {
        }

        public CachedCsvReader(TextReader reader, bool hasHeaders, int bufferSize) : this(reader, hasHeaders, ',', '"', '"', '#', true, bufferSize)
        {
        }

        public CachedCsvReader(TextReader reader, bool hasHeaders, char delimiter, int bufferSize) : this(reader, hasHeaders, delimiter, '"', '"', '#', true, bufferSize)
        {
        }

        public CachedCsvReader(TextReader reader, bool hasHeaders, char delimiter, char quote, char escape, char comment, bool trimSpaces) : this(reader, hasHeaders, delimiter, quote, escape, comment, trimSpaces, 0x1000)
        {
        }

        public CachedCsvReader(TextReader reader, bool hasHeaders, char delimiter, char quote, char escape, char comment, bool trimSpaces, int bufferSize) : base(reader, hasHeaders, delimiter, quote, escape, comment, trimSpaces, bufferSize)
        {
            this._records = new List<string[]>();
            this._currentRecordIndex = -1L;
        }

        public override void MoveTo(long record)
        {
            if (record < -1L)
            {
                throw new ArgumentOutOfRangeException("record", record, ExceptionMessage.RecordIndexLessThanZero);
            }
            if (record <= base.CurrentRecordIndex)
            {
                this._currentRecordIndex = record;
            }
            else
            {
                this._currentRecordIndex = base.CurrentRecordIndex;
                long num = record - this._currentRecordIndex;
                while (true)
                {
                    long num1 = num;
                    num = num1 - 1L;
                    if ((num1 <= 0L) || !base.ReadNextRecord())
                    {
                        return;
                    }
                }
            }
        }

        public void MoveToLastCachedRecord()
        {
            this._currentRecordIndex = base.CurrentRecordIndex;
        }

        public void MoveToStart()
        {
            this._currentRecordIndex = -1L;
        }

        protected override bool ReadNextRecord(bool onlyReadHeaders, bool skipToNextLine)
        {
            bool flag;
            if (this._currentRecordIndex < base.CurrentRecordIndex)
            {
                this._currentRecordIndex += 1L;
                return true;
            }
            this._readingStream = true;
            try
            {
                bool flag1 = base.ReadNextRecord(onlyReadHeaders, skipToNextLine);
                if (!flag1)
                {
                    this._records.Capacity = this._records.Count;
                }
                else
                {
                    string[] array = new string[base.FieldCount];
                    base.CopyCurrentRecordTo(array);
                    this._records.Add(array);
                    this._currentRecordIndex += 1L;
                }
                flag = flag1;
            }
            finally
            {
                this._readingStream = false;
            }
            return flag;
        }

        public virtual void ReadToEnd()
        {
            this._currentRecordIndex = base.CurrentRecordIndex;
            while (base.ReadNextRecord())
            {
            }
        }

        IList IListSource.GetList()
        {
            this._bindingList ??= new CsvBindingList(this);
            return this._bindingList;
        }

        public override long CurrentRecordIndex =>
            this._currentRecordIndex;

        public override bool EndOfStream =>
            (this._currentRecordIndex >= base.CurrentRecordIndex) ? base.EndOfStream : false;

        public override string this[int field]
        {
            get
            {
                if (this._readingStream)
                {
                    return base[field];
                }
                if (this._currentRecordIndex <= -1L)
                {
                    throw new InvalidOperationException(ExceptionMessage.NoCurrentRecord);
                }
                if ((field <= -1) || (field >= base.FieldCount))
                {
                    throw new ArgumentOutOfRangeException("field", field, string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.FieldIndexOutOfRange, field));
                }
                return this._records[(int) this._currentRecordIndex][field];
            }
        }

        bool IListSource.ContainsListCollection =>
            false;

        private class CsvBindingList : IBindingList, IList, ICollection, IEnumerable, ITypedList, IList<string[]>, ICollection<string[]>, IEnumerable<string[]>
        {
            private CachedCsvReader _csv;
            private int _count;
            private PropertyDescriptorCollection _properties;
            private CachedCsvReader.CsvPropertyDescriptor _sort;
            private ListSortDirection _direction;

            public event ListChangedEventHandler ListChanged
            {
                add
                {
                }
                remove
                {
                }
            }

            public CsvBindingList(CachedCsvReader csv)
            {
                this._csv = csv;
                this._count = -1;
                this._direction = ListSortDirection.Ascending;
            }

            public int Add(object value)
            {
                throw new NotSupportedException();
            }

            public void Add(string[] item)
            {
                throw new NotSupportedException();
            }

            public void AddIndex(PropertyDescriptor property)
            {
            }

            public object AddNew()
            {
                throw new NotSupportedException();
            }

            public void ApplySort(PropertyDescriptor property, ListSortDirection direction)
            {
                this._sort = (CachedCsvReader.CsvPropertyDescriptor) property;
                this._direction = direction;
                this._csv.ReadToEnd();
                this._csv._records.Sort(new CachedCsvReader.CsvRecordComparer(this._sort.Index, this._direction));
            }

            public void Clear()
            {
                throw new NotSupportedException();
            }

            public bool Contains(string[] item)
            {
                throw new NotSupportedException();
            }

            public bool Contains(object value)
            {
                throw new NotSupportedException();
            }

            public void CopyTo(string[][] array, int arrayIndex)
            {
                this._csv.MoveToStart();
                while (this._csv.ReadNextRecord())
                {
                    this._csv.CopyCurrentRecordTo(array[arrayIndex++]);
                }
            }

            public void CopyTo(Array array, int index)
            {
                this._csv.MoveToStart();
                while (this._csv.ReadNextRecord())
                {
                    this._csv.CopyCurrentRecordTo((string[]) array.GetValue(index++));
                }
            }

            public int Find(PropertyDescriptor property, object key)
            {
                int index = ((CachedCsvReader.CsvPropertyDescriptor) property).Index;
                string str = (string) key;
                int num2 = 0;
                int count = this.Count;
                while ((num2 < count) && (this._csv[num2, index] != str))
                {
                    num2++;
                }
                return ((num2 != count) ? num2 : -1);
            }

            public IEnumerator<string[]> GetEnumerator() => 
                this._csv.GetEnumerator();

            public PropertyDescriptorCollection GetItemProperties(PropertyDescriptor[] listAccessors)
            {
                if (this._properties == null)
                {
                    PropertyDescriptor[] properties = new PropertyDescriptor[this._csv.FieldCount];
                    int index = 0;
                    while (true)
                    {
                        if (index >= properties.Length)
                        {
                            this._properties = new PropertyDescriptorCollection(properties);
                            break;
                        }
                        properties[index] = new CachedCsvReader.CsvPropertyDescriptor(((IDataRecord) this._csv).GetName(index), index);
                        index++;
                    }
                }
                return this._properties;
            }

            public string GetListName(PropertyDescriptor[] listAccessors) => 
                string.Empty;

            public int IndexOf(string[] item)
            {
                throw new NotSupportedException();
            }

            public int IndexOf(object value)
            {
                throw new NotSupportedException();
            }

            public void Insert(int index, string[] item)
            {
                throw new NotSupportedException();
            }

            public void Insert(int index, object value)
            {
                throw new NotSupportedException();
            }

            public bool Remove(string[] item)
            {
                throw new NotSupportedException();
            }

            public void Remove(object value)
            {
                throw new NotSupportedException();
            }

            public void RemoveAt(int index)
            {
                throw new NotSupportedException();
            }

            public void RemoveIndex(PropertyDescriptor property)
            {
            }

            public void RemoveSort()
            {
                this._sort = null;
                this._direction = ListSortDirection.Ascending;
            }

            IEnumerator IEnumerable.GetEnumerator() => 
                this.GetEnumerator();

            public bool AllowNew =>
                false;

            public PropertyDescriptor SortProperty =>
                this._sort;

            public bool SupportsSorting =>
                true;

            public bool IsSorted =>
                this._sort != null;

            public bool AllowRemove =>
                false;

            public bool SupportsSearching =>
                true;

            public ListSortDirection SortDirection =>
                this._direction;

            public bool SupportsChangeNotification =>
                false;

            public bool AllowEdit =>
                false;

            public string[] this[int index]
            {
                get
                {
                    this._csv.MoveTo((long) index);
                    return this._csv._records[index];
                }
                set
                {
                    throw new NotSupportedException();
                }
            }

            public int Count
            {
                get
                {
                    if (this._count < 0)
                    {
                        this._csv.ReadToEnd();
                        this._count = ((int) this._csv.CurrentRecordIndex) + 1;
                    }
                    return this._count;
                }
            }

            public bool IsReadOnly =>
                true;

            public bool IsFixedSize =>
                true;

            object IList.this[int index]
            {
                get => 
                    this[index];
                set
                {
                    throw new NotSupportedException();
                }
            }

            public bool IsSynchronized =>
                false;

            public object SyncRoot =>
                null;
        }

        private class CsvPropertyDescriptor : PropertyDescriptor
        {
            private int _index;

            public CsvPropertyDescriptor(string fieldName, int index) : base(fieldName, null)
            {
                this._index = index;
            }

            public override bool CanResetValue(object component) => 
                false;

            public override object GetValue(object component) => 
                ((string[]) component)[this._index];

            public override void ResetValue(object component)
            {
            }

            public override void SetValue(object component, object value)
            {
            }

            public override bool ShouldSerializeValue(object component) => 
                false;

            public int Index =>
                this._index;

            public override Type ComponentType =>
                typeof(CachedCsvReader);

            public override bool IsReadOnly =>
                true;

            public override Type PropertyType =>
                typeof(string);
        }

        private class CsvRecordComparer : IComparer<string[]>
        {
            private int _field;
            private ListSortDirection _direction;

            public CsvRecordComparer(int field, ListSortDirection direction)
            {
                if (field < 0)
                {
                    throw new ArgumentOutOfRangeException("field", field, string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.FieldIndexOutOfRange, field));
                }
                this._field = field;
                this._direction = direction;
            }

            public int Compare(string[] x, string[] y)
            {
                int num = string.Compare(x[this._field], y[this._field], StringComparison.CurrentCulture);
                return ((this._direction == ListSortDirection.Ascending) ? num : -num);
            }
        }
    }
}

