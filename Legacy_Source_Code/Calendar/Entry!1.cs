namespace DMEWorks.Calendar
{
    using System;

    internal class Entry<TValue>
    {
        private TValue _value;
        private string _text;

        public Entry(TValue value, string text)
        {
            this._value = value;
            string text1 = text;
            if (text == null)
            {
                string local1 = text;
                text1 = "";
            }
            this._text = text1;
        }

        public TValue Value =>
            this._value;

        public string Text =>
            this._text;
    }
}

