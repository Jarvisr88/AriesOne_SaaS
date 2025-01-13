namespace DMEWorks.Controls
{
    using DMEWorks.Forms.Maps;
    using System;
    using System.Runtime.CompilerServices;

    public class MapProviderEventArgs : EventArgs
    {
        public MapProviderEventArgs(MapProvider provider)
        {
            if (provider == null)
            {
                MapProvider local1 = provider;
                throw new ArgumentNullException("provider");
            }
            this.<Provider>k__BackingField = provider;
        }

        public MapProvider Provider { get; }
    }
}

