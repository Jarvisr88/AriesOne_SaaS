namespace DMEWorks.Csv
{
    using DMEWorks.Csv.Resources;
    using System;
    using System.Collections;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Data;
    using System.Data.Common;
    using System.Globalization;
    using System.IO;
    using System.Reflection;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;
    using System.Threading;

    public class CsvReader : IDataReader, IDisposable, IDataRecord, IEnumerable<string[]>, IEnumerable
    {
        public const int DefaultBufferSize = 0x1000;
        public const char DefaultDelimiter = ',';
        public const char DefaultQuote = '"';
        public const char DefaultEscape = '"';
        public const char DefaultComment = '#';
        private static readonly StringComparer _fieldHeaderComparer = StringComparer.CurrentCultureIgnoreCase;
        private TextReader _reader;
        private int _bufferSize;
        private char _comment;
        private char _escape;
        private char _delimiter;
        private char _quote;
        private bool _trimSpaces;
        private bool _hasHeaders;
        private ParseErrorAction _defaultParseErrorAction;
        private DMEWorks.Csv.MissingFieldAction _missingFieldAction;
        private bool _supportsMultiline;
        private bool _initialized;
        private string[] _fieldHeaders;
        private Dictionary<string, int> _fieldHeaderIndexes;
        private long _currentRecordIndex;
        private int _nextFieldStart;
        private int _nextFieldIndex;
        private string[] _fields;
        private int _fieldCount;
        private char[] _buffer;
        private int _bufferLength;
        private bool _eof;
        private bool _firstRecordInCache;
        private bool _isDisposed;
        private readonly object _lock;

        public event EventHandler Disposed;

        public event EventHandler<ParseErrorEventArgs> ParseError;

        public CsvReader(TextReader reader, bool hasHeaders) : this(reader, hasHeaders, ',', '"', '"', '#', true, 0x1000)
        {
        }

        public CsvReader(TextReader reader, bool hasHeaders, char delimiter) : this(reader, hasHeaders, delimiter, '"', '"', '#', true, 0x1000)
        {
        }

        public CsvReader(TextReader reader, bool hasHeaders, int bufferSize) : this(reader, hasHeaders, ',', '"', '"', '#', true, bufferSize)
        {
        }

        public CsvReader(TextReader reader, bool hasHeaders, char delimiter, int bufferSize) : this(reader, hasHeaders, delimiter, '"', '"', '#', true, bufferSize)
        {
        }

        public CsvReader(TextReader reader, bool hasHeaders, char delimiter, char quote, char escape, char comment, bool trimSpaces) : this(reader, hasHeaders, delimiter, quote, escape, comment, trimSpaces, 0x1000)
        {
        }

        public CsvReader(TextReader reader, bool hasHeaders, char delimiter, char quote, char escape, char comment, bool trimSpaces, int bufferSize)
        {
            this._lock = new object();
            if (reader == null)
            {
                throw new ArgumentNullException("reader");
            }
            if (bufferSize <= 0)
            {
                throw new ArgumentOutOfRangeException("bufferSize", bufferSize, ExceptionMessage.BufferSizeTooSmall);
            }
            if (reader is StreamReader)
            {
                long length = ((StreamReader) reader).BaseStream.Length;
                this._bufferSize = (length <= 0L) ? bufferSize : ((int) Math.Min((long) bufferSize, length));
            }
            else
            {
                this._bufferSize = bufferSize;
            }
            this._reader = reader;
            this._delimiter = delimiter;
            this._quote = quote;
            this._escape = escape;
            this._comment = comment;
            this._hasHeaders = hasHeaders;
            this._trimSpaces = trimSpaces;
            this._supportsMultiline = true;
            this._currentRecordIndex = -1L;
            this._defaultParseErrorAction = ParseErrorAction.RaiseEvent;
        }

        protected void CheckDisposed()
        {
            if (this._isDisposed)
            {
                throw new ObjectDisposedException(base.GetType().FullName);
            }
        }

        public void CopyCurrentRecordTo(string[] array)
        {
            this.CopyCurrentRecordTo(array, 0);
        }

        public void CopyCurrentRecordTo(string[] array, int index)
        {
            if (array == null)
            {
                throw new ArgumentNullException("array");
            }
            if ((index < 0) || (index >= array.Length))
            {
                throw new ArgumentOutOfRangeException("index", index, string.Empty);
            }
            if ((this._currentRecordIndex < 0L) || !this._initialized)
            {
                throw new InvalidOperationException(ExceptionMessage.NoCurrentRecord);
            }
            if ((array.Length - index) < this._fieldCount)
            {
                throw new ArgumentException(ExceptionMessage.NotEnoughSpaceInArray, "array");
            }
            for (int i = 0; i < this._fieldCount; i++)
            {
                array[index + i] = this[i];
            }
        }

        private long CopyFieldToArray(int field, long fieldOffset, Array destinationArray, int destinationOffset, int length)
        {
            this.EnsureInitialize();
            if ((field < 0) || (field >= this._fieldCount))
            {
                throw new ArgumentOutOfRangeException("field", field, string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.FieldIndexOutOfRange, field));
            }
            if ((fieldOffset < 0L) || (fieldOffset >= 0x7fffffffL))
            {
                throw new ArgumentOutOfRangeException("fieldOffset");
            }
            if (length == 0)
            {
                return 0L;
            }
            string str = this[field];
            str ??= string.Empty;
            if (destinationArray.GetType() == typeof(char[]))
            {
                Array.Copy(str.ToCharArray((int) fieldOffset, length), 0, destinationArray, destinationOffset, length);
            }
            else
            {
                char[] chArray = str.ToCharArray((int) fieldOffset, length);
                byte[] sourceArray = new byte[chArray.Length];
                int index = 0;
                while (true)
                {
                    if (index >= chArray.Length)
                    {
                        Array.Copy(sourceArray, 0, destinationArray, destinationOffset, length);
                        break;
                    }
                    sourceArray[index] = Convert.ToByte(chArray[index]);
                    index++;
                }
            }
            return (long) length;
        }

        public void Dispose()
        {
            if (!this._isDisposed)
            {
                this.Dispose(true);
                GC.SuppressFinalize(this);
            }
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!this._isDisposed)
            {
                try
                {
                    if (disposing && (this._reader != null))
                    {
                        object obj2 = this._lock;
                        lock (obj2)
                        {
                            if (this._reader != null)
                            {
                                this._reader.Dispose();
                                this._reader = null;
                                this._buffer = null;
                                this._eof = true;
                            }
                        }
                    }
                }
                finally
                {
                    this._isDisposed = true;
                    try
                    {
                        this.OnDisposed(EventArgs.Empty);
                    }
                    catch
                    {
                    }
                }
            }
        }

        private void DoSkipBlankAndCommentedLines(ref int pos)
        {
            while (true)
            {
                if (pos < this._bufferLength)
                {
                    if (this._buffer[pos] == this._comment)
                    {
                        pos++;
                        this.SkipToNextLine(ref pos);
                        continue;
                    }
                    if (this.ParseNewLine(ref pos))
                    {
                        continue;
                    }
                }
                return;
            }
        }

        private void EnsureInitialize()
        {
            if (!this._initialized)
            {
                this.ReadNextRecord(true, false);
            }
        }

        ~CsvReader()
        {
            this.Dispose(false);
        }

        public string GetCurrentRawData() => 
            ((this._buffer == null) || (this._bufferLength <= 0)) ? string.Empty : new string(this._buffer, 0, this._bufferLength);

        public RecordEnumerator GetEnumerator() => 
            new RecordEnumerator(this);

        public string[] GetFieldHeaders()
        {
            this.EnsureInitialize();
            string[] strArray = new string[this._fieldHeaders.Length];
            for (int i = 0; i < strArray.Length; i++)
            {
                strArray[i] = this._fieldHeaders[i];
            }
            return strArray;
        }

        public int GetFieldIndex(string header)
        {
            int num;
            this.EnsureInitialize();
            return (((this._fieldHeaderIndexes == null) || !this._fieldHeaderIndexes.TryGetValue(header, out num)) ? -1 : num);
        }

        private string HandleMissingField(string value, int fieldIndex, ref int currentPosition)
        {
            if ((fieldIndex < 0) || (fieldIndex >= this._fieldCount))
            {
                throw new ArgumentOutOfRangeException("fieldIndex", fieldIndex, string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.FieldIndexOutOfRange, fieldIndex));
            }
            this._nextFieldIndex = this._fieldCount;
            switch (this._missingFieldAction)
            {
                case DMEWorks.Csv.MissingFieldAction.TreatAsParseError:
                    this.HandleParseError(new MissingFieldCsvException(this.GetCurrentRawData(), currentPosition, this._currentRecordIndex, fieldIndex), ref currentPosition);
                    return null;

                case DMEWorks.Csv.MissingFieldAction.ReturnEmptyValue:
                    return string.Empty;

                case DMEWorks.Csv.MissingFieldAction.ReturnNullValue:
                    return null;

                case DMEWorks.Csv.MissingFieldAction.ReturnPartiallyParsedValue:
                    return value;
            }
            throw new NotSupportedException(string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.MissingFieldActionNotSupported, this._missingFieldAction));
        }

        private void HandleParseError(MalformedCsvException error, ref int pos)
        {
            if (error == null)
            {
                throw new ArgumentNullException("error");
            }
            switch (this._defaultParseErrorAction)
            {
                case ParseErrorAction.RaiseEvent:
                {
                    ParseErrorEventArgs e = new ParseErrorEventArgs(error, ParseErrorAction.ThrowException);
                    this.OnParseError(e);
                    switch (e.Action)
                    {
                        case ParseErrorAction.RaiseEvent:
                            throw new InvalidOperationException(string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.ParseErrorActionInvalidInsideParseErrorEvent, e.Action), e.Error);

                        case ParseErrorAction.AdvanceToNextLine:
                            if (pos < 0)
                            {
                                break;
                            }
                            this.ReadNextRecord(false, true);
                            return;

                        case ParseErrorAction.ThrowException:
                            throw e.Error;

                        default:
                            throw new NotSupportedException(string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.ParseErrorActionNotSupported, e.Action), e.Error);
                    }
                    break;
                }
                case ParseErrorAction.AdvanceToNextLine:
                    if (pos < 0)
                    {
                        break;
                    }
                    this.ReadNextRecord(false, true);
                    return;

                case ParseErrorAction.ThrowException:
                    throw error;

                default:
                    throw new NotSupportedException(string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.ParseErrorActionNotSupported, this._defaultParseErrorAction), error);
            }
        }

        private bool IsWhiteSpace(char c) => 
            (c != this._delimiter) ? ((c > '\x00ff') ? (CharUnicodeInfo.GetUnicodeCategory(c) == UnicodeCategory.SpaceSeparator) : ((c == ' ') || (c == '\t'))) : false;

        public virtual void MoveTo(long record)
        {
            if (record < 0L)
            {
                throw new ArgumentOutOfRangeException("record", record, ExceptionMessage.RecordIndexLessThanZero);
            }
            if (record < this._currentRecordIndex)
            {
                throw new InvalidOperationException(ExceptionMessage.CannotMovePreviousRecordInForwardOnly);
            }
            long num = record - this._currentRecordIndex;
            if (num > 0L)
            {
                long num1;
                do
                {
                    if (!this.ReadNextRecord())
                    {
                        throw new EndOfStreamException(string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.CannotReadRecordAtIndex, this._currentRecordIndex - num));
                    }
                    num1 = num - 1L;
                }
                while ((num = num1) > 0L);
            }
        }

        protected virtual void OnDisposed(EventArgs e)
        {
            EventHandler disposed = this.Disposed;
            if (disposed != null)
            {
                disposed(this, e);
            }
        }

        protected virtual void OnParseError(ParseErrorEventArgs e)
        {
            EventHandler<ParseErrorEventArgs> parseError = this.ParseError;
            if (parseError != null)
            {
                parseError(this, e);
            }
        }

        private bool ParseNewLine(ref int pos)
        {
            if (pos == this._bufferLength)
            {
                pos = 0;
                if (!this.ReadBuffer())
                {
                    return false;
                }
            }
            char ch = this._buffer[pos];
            if ((ch != '\r') || (this._delimiter == '\r'))
            {
                if (ch != '\n')
                {
                    return false;
                }
                pos++;
                return true;
            }
            pos++;
            if (pos < this._bufferLength)
            {
                if (this._buffer[pos] == '\n')
                {
                    pos++;
                }
            }
            else if (this.ReadBuffer())
            {
                pos = (this._buffer[0] != '\n') ? 0 : 1;
            }
            return true;
        }

        private bool ReadBuffer()
        {
            if (!this._eof)
            {
                this.CheckDisposed();
                this._bufferLength = this._reader.Read(this._buffer, 0, this._bufferSize);
                if (this._bufferLength > 0)
                {
                    return true;
                }
                this._eof = true;
                this._buffer = null;
            }
            return false;
        }

        private string ReadField(int field, bool initializing, bool discardValue)
        {
            string str;
            bool flag;
            int num4;
            int num5;
            bool flag2;
            bool flag3;
            if (!initializing)
            {
                if ((field < 0) || (field >= this._fieldCount))
                {
                    throw new ArgumentOutOfRangeException("field", field, string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.FieldIndexOutOfRange, field));
                }
                if (this._currentRecordIndex < 0L)
                {
                    throw new InvalidOperationException(ExceptionMessage.NoCurrentRecord);
                }
            }
            if (this._fields[field] != null)
            {
                return this._fields[field];
            }
            if (field < this._nextFieldIndex)
            {
                return this.HandleMissingField(string.Empty, field, ref this._nextFieldStart);
            }
            this.CheckDisposed();
            int currentFieldIndex = this._nextFieldIndex;
            goto TR_005D;
        TR_0006:
            this._nextFieldIndex = (initializing || (currentFieldIndex < (this._fieldCount - 1))) ? Math.Max(currentFieldIndex + 1, this._nextFieldIndex) : 0;
            if (currentFieldIndex == field)
            {
                return ((!initializing || (!flag && !this._eof)) ? str : null);
            }
            currentFieldIndex++;
        TR_005D:
            while (true)
            {
                if (currentFieldIndex >= (field + 1))
                {
                    this.HandleParseError(new MalformedCsvException(this.GetCurrentRawData(), this._nextFieldStart, this._currentRecordIndex, currentFieldIndex), ref this._nextFieldStart);
                    return null;
                }
                if (this._nextFieldStart == this._bufferLength)
                {
                    this._nextFieldStart = 0;
                    this.ReadBuffer();
                }
                str = null;
                flag = false;
                if (this._nextFieldStart == this._bufferLength)
                {
                    if (currentFieldIndex != field)
                    {
                        str = this.HandleMissingField(str, currentFieldIndex, ref this._nextFieldStart);
                    }
                    else if (!discardValue)
                    {
                        str = string.Empty;
                        this._fields[currentFieldIndex] = str;
                    }
                }
                else
                {
                    if (this._trimSpaces)
                    {
                        this.SkipWhiteSpaces(ref this._nextFieldStart);
                    }
                    if (this._buffer[this._nextFieldStart] == this._quote)
                    {
                        num4 = this._nextFieldStart + 1;
                        num5 = num4;
                        flag2 = true;
                        flag3 = false;
                        break;
                    }
                    int startIndex = this._nextFieldStart;
                    int index = this._nextFieldStart;
                    do
                    {
                        if (index < this._bufferLength)
                        {
                            char ch = this._buffer[index];
                            if (ch == this._delimiter)
                            {
                                this._nextFieldStart = index + 1;
                            }
                            else
                            {
                                if ((ch != '\r') && (ch != '\n'))
                                {
                                    index++;
                                    continue;
                                }
                                this._nextFieldStart = index;
                                flag = true;
                            }
                        }
                        if (index < this._bufferLength)
                        {
                            break;
                        }
                        if (!discardValue)
                        {
                            str = str + new string(this._buffer, startIndex, index - startIndex);
                        }
                        startIndex = 0;
                        index = 0;
                        this._nextFieldStart = 0;
                    }
                    while (this.ReadBuffer());
                    if (!discardValue)
                    {
                        if (!this._trimSpaces)
                        {
                            if (!this._eof && (index > startIndex))
                            {
                                str = str + new string(this._buffer, startIndex, index - startIndex);
                            }
                        }
                        else
                        {
                            if (this._eof || (index <= startIndex))
                            {
                                index = -1;
                            }
                            else
                            {
                                index--;
                                while (true)
                                {
                                    if ((index <= -1) || !this.IsWhiteSpace(this._buffer[index]))
                                    {
                                        index++;
                                        if (index > 0)
                                        {
                                            str = str + new string(this._buffer, startIndex, index - startIndex);
                                        }
                                        break;
                                    }
                                    index--;
                                }
                            }
                            if (index < 0)
                            {
                                index = (str == null) ? -1 : (str.Length - 1);
                                while (true)
                                {
                                    if ((index <= -1) || !this.IsWhiteSpace(str[index]))
                                    {
                                        index++;
                                        if ((index > 0) && (index != str.Length))
                                        {
                                            str = str.Substring(0, index);
                                        }
                                        break;
                                    }
                                    index--;
                                }
                            }
                        }
                        str ??= string.Empty;
                    }
                    if (flag || this._eof)
                    {
                        if (!initializing && (currentFieldIndex != (this._fieldCount - 1)))
                        {
                            str = this.HandleMissingField(str, currentFieldIndex, ref this._nextFieldStart);
                        }
                        else
                        {
                            flag = this.ParseNewLine(ref this._nextFieldStart);
                        }
                    }
                    if (!discardValue)
                    {
                        this._fields[currentFieldIndex] = str;
                    }
                }
                goto TR_0006;
            }
        TR_0053:
            while (num5 < this._bufferLength)
            {
                char ch2 = this._buffer[num5];
                if (flag3)
                {
                    flag3 = false;
                    num4 = num5;
                }
                else if ((ch2 != this._escape) || (((this._escape == this._quote) && (((num5 + 1) >= this._bufferLength) || (this._buffer[num5 + 1] != this._quote))) && (((num5 + 1) != this._bufferLength) || (this._reader.Peek() != this._quote))))
                {
                    if (ch2 == this._quote)
                    {
                        flag2 = false;
                        break;
                    }
                }
                else
                {
                    if (!discardValue)
                    {
                        str = str + new string(this._buffer, num4, num5 - num4);
                    }
                    flag3 = true;
                }
                num5++;
            }
            if (!flag2)
            {
                if (!this._eof)
                {
                    if (!discardValue && (num5 > num4))
                    {
                        str = str + new string(this._buffer, num4, num5 - num4);
                    }
                    this._nextFieldStart = num5 + 1;
                    this.SkipWhiteSpaces(ref this._nextFieldStart);
                    if ((this._nextFieldStart < this._bufferLength) && (this._buffer[this._nextFieldStart] == this._delimiter))
                    {
                        this._nextFieldStart++;
                    }
                    if (!this._eof && (initializing || (currentFieldIndex == (this._fieldCount - 1))))
                    {
                        flag = this.ParseNewLine(ref this._nextFieldStart);
                    }
                }
                if (!discardValue)
                {
                    str ??= string.Empty;
                    this._fields[currentFieldIndex] = str;
                }
            }
            else
            {
                if (!discardValue && !flag3)
                {
                    str = str + new string(this._buffer, num4, num5 - num4);
                }
                num4 = 0;
                num5 = 0;
                this._nextFieldStart = 0;
                if (!this.ReadBuffer())
                {
                    this.HandleParseError(new MalformedCsvException(this.GetCurrentRawData(), this._nextFieldStart, this._currentRecordIndex, currentFieldIndex), ref this._nextFieldStart);
                    return null;
                }
                goto TR_0053;
            }
            goto TR_0006;
        }

        public bool ReadNextRecord() => 
            this.ReadNextRecord(false, false);

        protected virtual bool ReadNextRecord(bool onlyReadHeaders, bool skipToNextLine)
        {
            if (this._eof)
            {
                if (!this._firstRecordInCache)
                {
                    return false;
                }
                this._firstRecordInCache = false;
                this._currentRecordIndex += 1L;
                return true;
            }
            this.CheckDisposed();
            if (this._initialized)
            {
                if (skipToNextLine)
                {
                    this.SkipToNextLine(ref this._nextFieldStart);
                }
                else if (this._currentRecordIndex > -1L)
                {
                    if (this._supportsMultiline)
                    {
                        this.ReadField(this._fieldCount - 1, false, true);
                    }
                    else if ((this._nextFieldIndex > 0) && (this._nextFieldIndex < this._fieldCount))
                    {
                        this.SkipToNextLine(ref this._nextFieldStart);
                    }
                }
                if (!this.SkipBlankAndCommentedLines(ref this._nextFieldStart))
                {
                    return false;
                }
                if (this._firstRecordInCache)
                {
                    this._firstRecordInCache = false;
                }
                else
                {
                    Array.Clear(this._fields, 0, this._fields.Length);
                    this._nextFieldIndex = 0;
                }
                this._currentRecordIndex += 1L;
            }
            else
            {
                this._buffer = new char[this._bufferSize];
                if (!this.ReadBuffer())
                {
                    return false;
                }
                if (!this.SkipBlankAndCommentedLines(ref this._nextFieldStart))
                {
                    return false;
                }
                this._fieldCount = 0;
                this._fields = new string[0x10];
                while (true)
                {
                    if (this.ReadField(this._fieldCount, true, false) == null)
                    {
                        this._fieldCount++;
                        if (this._fields.Length != this._fieldCount)
                        {
                            Array.Resize<string>(ref this._fields, this._fieldCount);
                        }
                        this._initialized = true;
                        if (!this._hasHeaders)
                        {
                            if (onlyReadHeaders)
                            {
                                this._firstRecordInCache = true;
                                this._currentRecordIndex = -1L;
                            }
                            else
                            {
                                this._firstRecordInCache = false;
                                this._currentRecordIndex = 0L;
                            }
                            this._fieldHeaders = new string[0];
                        }
                        else
                        {
                            this._currentRecordIndex = -1L;
                            this._firstRecordInCache = false;
                            this._fieldHeaders = new string[this._fieldCount];
                            this._fieldHeaderIndexes = new Dictionary<string, int>(this._fieldCount, _fieldHeaderComparer);
                            int index = 0;
                            while (true)
                            {
                                if (index >= this._fields.Length)
                                {
                                    if (onlyReadHeaders)
                                    {
                                        break;
                                    }
                                    if (!this.SkipBlankAndCommentedLines(ref this._nextFieldStart))
                                    {
                                        return false;
                                    }
                                    Array.Clear(this._fields, 0, this._fields.Length);
                                    this._nextFieldIndex = 0;
                                    this._currentRecordIndex += 1L;
                                    return true;
                                }
                                this._fieldHeaders[index] = this._fields[index];
                                this._fieldHeaderIndexes.Add(this._fields[index], index);
                                index++;
                            }
                        }
                        break;
                    }
                    this._fieldCount++;
                    if (this._fieldCount == this._fields.Length)
                    {
                        Array.Resize<string>(ref this._fields, (this._fieldCount + 1) * 2);
                    }
                }
            }
            return true;
        }

        private bool SkipBlankAndCommentedLines(ref int pos)
        {
            if (pos < this._bufferLength)
            {
                this.DoSkipBlankAndCommentedLines(ref pos);
            }
            while ((pos >= this._bufferLength) && !this._eof)
            {
                if (!this.ReadBuffer())
                {
                    return false;
                }
                pos = 0;
                this.DoSkipBlankAndCommentedLines(ref pos);
            }
            return !this._eof;
        }

        private bool SkipToNextLine(ref int pos)
        {
            while (true)
            {
                if (pos >= this._bufferLength)
                {
                    if (!this.ReadBuffer())
                    {
                        break;
                    }
                    if ((pos = 0) != 0)
                    {
                        break;
                    }
                }
                if (this.ParseNewLine(ref pos))
                {
                    break;
                }
                pos++;
            }
            return !this._eof;
        }

        private bool SkipWhiteSpaces(ref int pos)
        {
            while (true)
            {
                if ((pos < this._bufferLength) && this.IsWhiteSpace(this._buffer[pos]))
                {
                    pos++;
                    continue;
                }
                if (pos < this._bufferLength)
                {
                    return true;
                }
                pos = 0;
                if (!this.ReadBuffer())
                {
                    return false;
                }
            }
        }

        IEnumerator<string[]> IEnumerable<string[]>.GetEnumerator() => 
            this.GetEnumerator();

        IEnumerator IEnumerable.GetEnumerator() => 
            this.GetEnumerator();

        void IDataReader.Close()
        {
            this.Dispose();
        }

        DataTable IDataReader.GetSchemaTable()
        {
            string[] strArray;
            this.EnsureInitialize();
            this.ValidateDataReader(DataReaderValidations.IsNotClosed);
            DataTable table = new DataTable("SchemaTable") {
                Locale = CultureInfo.InvariantCulture,
                MinimumCapacity = this._fieldCount
            };
            table.Columns.Add(SchemaTableColumn.AllowDBNull, typeof(bool)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.BaseColumnName, typeof(string)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.BaseSchemaName, typeof(string)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.BaseTableName, typeof(string)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.ColumnName, typeof(string)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.ColumnOrdinal, typeof(int)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.ColumnSize, typeof(int)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.DataType, typeof(object)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.IsAliased, typeof(bool)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.IsExpression, typeof(bool)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.IsKey, typeof(bool)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.IsLong, typeof(bool)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.IsUnique, typeof(bool)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.NumericPrecision, typeof(short)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.NumericScale, typeof(short)).ReadOnly = true;
            table.Columns.Add(SchemaTableColumn.ProviderType, typeof(int)).ReadOnly = true;
            table.Columns.Add(SchemaTableOptionalColumn.BaseCatalogName, typeof(string)).ReadOnly = true;
            table.Columns.Add(SchemaTableOptionalColumn.BaseServerName, typeof(string)).ReadOnly = true;
            table.Columns.Add(SchemaTableOptionalColumn.IsAutoIncrement, typeof(bool)).ReadOnly = true;
            table.Columns.Add(SchemaTableOptionalColumn.IsHidden, typeof(bool)).ReadOnly = true;
            table.Columns.Add(SchemaTableOptionalColumn.IsReadOnly, typeof(bool)).ReadOnly = true;
            table.Columns.Add(SchemaTableOptionalColumn.IsRowVersion, typeof(bool)).ReadOnly = true;
            if (this._hasHeaders)
            {
                strArray = this._fieldHeaders;
            }
            else
            {
                strArray = new string[this._fieldCount];
                for (int j = 0; j < this._fieldCount; j++)
                {
                    strArray[j] = "Column" + j.ToString(CultureInfo.InvariantCulture);
                }
            }
            object[] objArray1 = new object[0x16];
            objArray1[0] = true;
            objArray1[2] = string.Empty;
            objArray1[3] = string.Empty;
            objArray1[6] = 0x7fffffff;
            objArray1[7] = typeof(string);
            objArray1[8] = false;
            objArray1[9] = false;
            objArray1[10] = false;
            objArray1[11] = false;
            objArray1[12] = false;
            objArray1[13] = DBNull.Value;
            objArray1[14] = DBNull.Value;
            objArray1[15] = 0x10;
            objArray1[0x10] = string.Empty;
            objArray1[0x11] = string.Empty;
            objArray1[0x12] = false;
            objArray1[0x13] = false;
            objArray1[20] = true;
            objArray1[0x15] = false;
            object[] values = objArray1;
            for (int i = 0; i < strArray.Length; i++)
            {
                values[1] = strArray[i];
                values[4] = strArray[i];
                values[5] = i;
                table.Rows.Add(values);
            }
            return table;
        }

        bool IDataReader.NextResult()
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed);
            return false;
        }

        bool IDataReader.Read()
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed);
            return this.ReadNextRecord();
        }

        bool IDataRecord.GetBoolean(int i)
        {
            int num;
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            string s = this[i];
            return (!int.TryParse(s, out num) ? bool.Parse(s) : (num != 0));
        }

        byte IDataRecord.GetByte(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return byte.Parse(this[i], CultureInfo.CurrentCulture);
        }

        long IDataRecord.GetBytes(int i, long fieldOffset, byte[] buffer, int bufferoffset, int length)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return this.CopyFieldToArray(i, fieldOffset, buffer, bufferoffset, length);
        }

        char IDataRecord.GetChar(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return char.Parse(this[i]);
        }

        long IDataRecord.GetChars(int i, long fieldoffset, char[] buffer, int bufferoffset, int length)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return this.CopyFieldToArray(i, fieldoffset, buffer, bufferoffset, length);
        }

        IDataReader IDataRecord.GetData(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return ((i != 0) ? null : this);
        }

        string IDataRecord.GetDataTypeName(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return typeof(string).FullName;
        }

        DateTime IDataRecord.GetDateTime(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return DateTime.Parse(this[i], CultureInfo.CurrentCulture);
        }

        decimal IDataRecord.GetDecimal(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return decimal.Parse(this[i], CultureInfo.CurrentCulture);
        }

        double IDataRecord.GetDouble(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return double.Parse(this[i], CultureInfo.CurrentCulture);
        }

        Type IDataRecord.GetFieldType(int i)
        {
            this.EnsureInitialize();
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            if ((i < 0) || (i >= this._fieldCount))
            {
                throw new ArgumentOutOfRangeException("i", i, string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.FieldIndexOutOfRange, i));
            }
            return typeof(string);
        }

        float IDataRecord.GetFloat(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return float.Parse(this[i], CultureInfo.CurrentCulture);
        }

        Guid IDataRecord.GetGuid(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return new Guid(this[i]);
        }

        short IDataRecord.GetInt16(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return short.Parse(this[i], CultureInfo.CurrentCulture);
        }

        int IDataRecord.GetInt32(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            string str = this[i];
            return int.Parse((str == null) ? string.Empty : str, CultureInfo.CurrentCulture);
        }

        long IDataRecord.GetInt64(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return long.Parse(this[i], CultureInfo.CurrentCulture);
        }

        string IDataRecord.GetName(int i)
        {
            this.EnsureInitialize();
            this.ValidateDataReader(DataReaderValidations.IsNotClosed);
            if ((i < 0) || (i >= this._fieldCount))
            {
                throw new ArgumentOutOfRangeException("i", i, string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.FieldIndexOutOfRange, i));
            }
            return (!this._hasHeaders ? ("Column" + i.ToString(CultureInfo.InvariantCulture)) : this._fieldHeaders[i]);
        }

        int IDataRecord.GetOrdinal(string name)
        {
            int num;
            this.EnsureInitialize();
            this.ValidateDataReader(DataReaderValidations.IsNotClosed);
            if (!this._fieldHeaderIndexes.TryGetValue(name, out num))
            {
                throw new ArgumentException(string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.FieldHeaderNotFound, name), "name");
            }
            return num;
        }

        string IDataRecord.GetString(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return this[i];
        }

        object IDataRecord.GetValue(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return this[i];
        }

        int IDataRecord.GetValues(object[] values)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            for (int i = 0; i < this._fieldCount; i++)
            {
                values[i] = this[i];
            }
            return this._fieldCount;
        }

        bool IDataRecord.IsDBNull(int i)
        {
            this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
            return string.IsNullOrEmpty(this[i]);
        }

        private void ValidateDataReader(DataReaderValidations validations)
        {
            if (((validations & DataReaderValidations.IsInitialized) != DataReaderValidations.None) && !this._initialized)
            {
                throw new InvalidOperationException(ExceptionMessage.NoCurrentRecord);
            }
            if (((validations & DataReaderValidations.IsNotClosed) != DataReaderValidations.None) && this._isDisposed)
            {
                throw new InvalidOperationException(ExceptionMessage.ReaderClosed);
            }
        }

        public char Comment =>
            this._comment;

        public char Escape =>
            this._escape;

        public char Delimiter =>
            this._delimiter;

        public char Quote =>
            this._quote;

        public bool HasHeaders =>
            this._hasHeaders;

        public bool TrimSpaces =>
            this._trimSpaces;

        public int BufferSize =>
            this._bufferSize;

        public ParseErrorAction DefaultParseErrorAction
        {
            get => 
                this._defaultParseErrorAction;
            set => 
                this._defaultParseErrorAction = value;
        }

        public DMEWorks.Csv.MissingFieldAction MissingFieldAction
        {
            get => 
                this._missingFieldAction;
            set => 
                this._missingFieldAction = value;
        }

        public bool SupportsMultiline
        {
            get => 
                this._supportsMultiline;
            set => 
                this._supportsMultiline = value;
        }

        public int FieldCount
        {
            get
            {
                this.EnsureInitialize();
                return this._fieldCount;
            }
        }

        public virtual bool EndOfStream =>
            this._eof;

        public virtual long CurrentRecordIndex =>
            this._currentRecordIndex;

        public string this[int record, string field]
        {
            get
            {
                this.MoveTo((long) record);
                return this[field];
            }
        }

        public string this[int record, int field]
        {
            get
            {
                this.MoveTo((long) record);
                return this[field];
            }
        }

        public string this[string field]
        {
            get
            {
                if (string.IsNullOrEmpty(field))
                {
                    throw new ArgumentNullException("field");
                }
                if (!this._hasHeaders)
                {
                    throw new InvalidOperationException(ExceptionMessage.NoHeaders);
                }
                int fieldIndex = this.GetFieldIndex(field);
                if (fieldIndex < 0)
                {
                    throw new ArgumentException(string.Format((IFormatProvider) CultureInfo.InvariantCulture, ExceptionMessage.FieldHeaderNotFound, field), "field");
                }
                return this[fieldIndex];
            }
        }

        public virtual string this[int field] =>
            this.ReadField(field, false, false);

        int IDataReader.RecordsAffected =>
            -1;

        bool IDataReader.IsClosed =>
            this._eof;

        int IDataReader.Depth
        {
            get
            {
                this.ValidateDataReader(DataReaderValidations.IsNotClosed);
                return 0;
            }
        }

        object IDataRecord.this[string name]
        {
            get
            {
                this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
                return this[name];
            }
        }

        object IDataRecord.this[int i]
        {
            get
            {
                this.ValidateDataReader(DataReaderValidations.IsNotClosed | DataReaderValidations.IsInitialized);
                return this[i];
            }
        }

        [Browsable(false)]
        public bool IsDisposed =>
            this._isDisposed;

        [Flags]
        private enum DataReaderValidations
        {
            None,
            IsInitialized,
            IsNotClosed
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct RecordEnumerator : IEnumerator<string[]>, IDisposable, IEnumerator
        {
            private CsvReader _reader;
            private string[] _current;
            private long _currentRecordIndex;
            public RecordEnumerator(CsvReader reader)
            {
                if (reader == null)
                {
                    throw new ArgumentNullException("reader");
                }
                this._reader = reader;
                this._current = null;
                this._currentRecordIndex = reader._currentRecordIndex;
            }

            public string[] Current =>
                this._current;
            public bool MoveNext()
            {
                if (this._reader._currentRecordIndex != this._currentRecordIndex)
                {
                    throw new InvalidOperationException(ExceptionMessage.EnumerationVersionCheckFailed);
                }
                if (!this._reader.ReadNextRecord())
                {
                    this._current = null;
                    this._currentRecordIndex = this._reader._currentRecordIndex;
                    return false;
                }
                this._current ??= new string[this._reader._fieldCount];
                this._reader.CopyCurrentRecordTo(this._current);
                this._currentRecordIndex = this._reader._currentRecordIndex;
                return true;
            }

            public void Reset()
            {
                if (this._reader._currentRecordIndex != this._currentRecordIndex)
                {
                    throw new InvalidOperationException(ExceptionMessage.EnumerationVersionCheckFailed);
                }
                this._reader.MoveTo(-1L);
                this._current = null;
                this._currentRecordIndex = this._reader._currentRecordIndex;
            }

            object IEnumerator.Current
            {
                get
                {
                    if (this._reader._currentRecordIndex != this._currentRecordIndex)
                    {
                        throw new InvalidOperationException(ExceptionMessage.EnumerationVersionCheckFailed);
                    }
                    return this.Current;
                }
            }
            public void Dispose()
            {
                this._reader = null;
                this._current = null;
            }
        }
    }
}

