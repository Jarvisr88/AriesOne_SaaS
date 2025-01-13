namespace DMEWorks.Core
{
    using DMEWorks.Forms;
    using System;
    using System.Runtime.CompilerServices;

    public class CreateSourceEventArgs : EventArgs
    {
        public IGridSource Source { get; set; }
    }
}

