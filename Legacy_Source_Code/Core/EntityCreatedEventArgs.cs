namespace DMEWorks.Core
{
    using System;
    using System.Runtime.CompilerServices;

    public class EntityCreatedEventArgs : EventArgs
    {
        public EntityCreatedEventArgs(object id)
        {
            this.<ID>k__BackingField = id;
        }

        public object ID { get; }
    }
}

