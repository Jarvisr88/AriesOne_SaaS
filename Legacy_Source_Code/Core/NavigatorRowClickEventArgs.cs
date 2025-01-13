namespace DMEWorks.Core
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Windows.Forms;

    public class NavigatorRowClickEventArgs : EventArgs
    {
        public NavigatorRowClickEventArgs(DataGridViewRow row)
        {
            if (row == null)
            {
                DataGridViewRow local1 = row;
                throw new ArgumentNullException("row");
            }
            this.GridRow = row;
        }

        public DataGridViewRow GridRow { get; private set; }
    }
}

