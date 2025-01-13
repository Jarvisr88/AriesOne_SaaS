namespace DMEWorks.Data.MySql
{
    using Devart.Data.MySql;
    using System;
    using System.Data;

    public abstract class MySqlDataAdapterEventsBase : IDisposable
    {
        protected readonly MySqlCommand cmdSelectIdentity;
        private MySqlDataAdapter dataAdapter;

        protected MySqlDataAdapterEventsBase(MySqlDataAdapter da)
        {
            if (da == null)
            {
                throw new ArgumentNullException("da");
            }
            this.dataAdapter = da;
            this.dataAdapter.RowUpdating += new MySqlRowUpdatingEventHandler(this.OnRowUpdating);
            this.dataAdapter.RowUpdated += new MySqlRowUpdatedEventHandler(this.OnRowUpdated);
            this.cmdSelectIdentity = new MySqlCommand();
            this.cmdSelectIdentity.CommandType = CommandType.Text;
            this.cmdSelectIdentity.CommandText = "SELECT LAST_INSERT_ID()";
        }

        public void Dispose()
        {
            this.cmdSelectIdentity.Dispose();
            this.dataAdapter.RowUpdating -= new MySqlRowUpdatingEventHandler(this.OnRowUpdating);
            this.dataAdapter.RowUpdated -= new MySqlRowUpdatedEventHandler(this.OnRowUpdated);
            this.dataAdapter = null;
        }

        protected void OnRowUpdated(object sender, MySqlRowUpdatedEventArgs e)
        {
            this.ProcessRowUpdated(e);
        }

        protected void OnRowUpdating(object sender, MySqlRowUpdatingEventArgs e)
        {
            this.ProcessRowUpdating(e);
        }

        protected abstract void ProcessRowUpdated(MySqlRowUpdatedEventArgs e);
        protected virtual void ProcessRowUpdating(MySqlRowUpdatingEventArgs e)
        {
        }
    }
}

