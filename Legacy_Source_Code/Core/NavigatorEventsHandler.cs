namespace DMEWorks.Core
{
    using DMEWorks.Forms;
    using System;
    using System.Collections.Generic;

    public abstract class NavigatorEventsHandler
    {
        protected NavigatorEventsHandler()
        {
        }

        public virtual void CreateSource(object sender, CreateSourceEventArgs args)
        {
            throw new NotImplementedException();
        }

        public virtual void FillSource(object sender, FillSourceEventArgs args)
        {
            throw new NotImplementedException();
        }

        public virtual void FillSource(object sender, PagedFillSourceEventArgs args)
        {
            throw new NotImplementedException();
        }

        public virtual void InitializeAppearance(GridAppearanceBase appearance)
        {
            throw new NotImplementedException();
        }

        public virtual void NavigatorRowClick(object sender, NavigatorRowClickEventArgs args)
        {
            throw new NotImplementedException();
        }

        public virtual string Caption =>
            "Search";

        public virtual bool Switchable =>
            true;

        public virtual IEnumerable<string> TableNames
        {
            get
            {
                throw new NotImplementedException();
            }
        }
    }
}

