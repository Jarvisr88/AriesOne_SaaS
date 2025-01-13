namespace DMEWorks.Core
{
    using System;
    using System.Runtime.CompilerServices;

    public class PagedFilter
    {
        public PagedFilter(string filter, int start, int count)
        {
            if (start < 0)
            {
                throw new ArgumentOutOfRangeException("start", "cannot be negative");
            }
            if (count < 0)
            {
                throw new ArgumentOutOfRangeException("count", "cannot be negative");
            }
            this.Filter = filter;
            this.Start = start;
            this.Count = count;
        }

        public int Count { get; set; }

        public string Filter { get; private set; }

        public int Start { get; private set; }
    }
}

