namespace DMEWorks.Core
{
    using DMEWorks.Forms;
    using System;
    using System.Runtime.CompilerServices;

    public class FillSourceEventArgs : EventArgs
    {
        public FillSourceEventArgs(IGridSource source)
        {
            if (source == null)
            {
                IGridSource local1 = source;
                throw new ArgumentNullException("source");
            }
            this.Source = source;
        }

        public IGridSource Source { get; set; }
    }
}

