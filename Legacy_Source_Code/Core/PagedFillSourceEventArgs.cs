namespace DMEWorks.Core
{
    using DMEWorks.Forms;
    using System;
    using System.Runtime.CompilerServices;

    public class PagedFillSourceEventArgs : FillSourceEventArgs
    {
        public PagedFillSourceEventArgs(IGridSource source, string filter) : base(source)
        {
            this.<Filter>k__BackingField = new PagedFilter(filter, source.Count, 100);
        }

        public PagedFilter Filter { get; }
    }
}

