namespace DMEWorks.Core
{
    using System;
    using System.Collections.Generic;
    using System.Runtime.CompilerServices;

    public abstract class NavigatorOptionsBase
    {
        protected NavigatorOptionsBase()
        {
        }

        public string Caption { get; set; }

        public EventHandler<CreateSourceEventArgs> CreateSource { get; set; }

        public Action<GridAppearanceBase> InitializeAppearance { get; set; }

        public EventHandler<NavigatorRowClickEventArgs> NavigatorRowClick { get; set; }

        public bool Switchable { get; set; }

        public IEnumerable<string> TableNames { get; set; }
    }
}

